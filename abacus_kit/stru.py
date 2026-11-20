"""STRU writer adapted from the ABACUS ASE interface (LGPL v3)."""
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from ase.atoms import Atoms
from ase.constraints import FixAtoms, FixCartesian
from ase.data import atomic_masses, chemical_symbols

ATOM_MASS = dict(zip(chemical_symbols, atomic_masses.tolist()))


def _write_stru(job_dir, stru, fname='STRU'):
    '''
    Generates a ABACUS STRU file from a STRU dict.

    Parameters
    ----------
    job_dir: str
        Directory in which the STRU file is generated.
    stru : dict
        Parameters to generate the STRU file.
        See the docstring at the beginning of this script for details.
    fname : str
        Name of the STRU file.

    '''
    with open(Path(job_dir) / fname, 'w') as f:

        #============ ATOMIC_SPECIES ============
        f.write('ATOMIC_SPECIES\n')
        width = {key + '_w' : max([len(str(s[key])) for s in stru['species']])
                 for key in ['symbol', 'mass', 'pp_file']}
        for s in stru['species']:
            f.write('{symbol:<{symbol_w}}  {mass:>{mass_w}}  {pp_file:>{pp_file_w}}'.format(**s, **width))
            if 'pp_type' in s:
                f.write(f"  {s['pp_type']}")
            f.write('\n')

        #============ NUMERICAL_ORBITAL ============
        if 'orb_file' in stru['species'][0]:
            f.write('\nNUMERICAL_ORBITAL\n')
            for s in stru['species']:
                f.write(f"{s['orb_file']}\n")

        #============ LATTICE_CONSTANT/PARAMETER/VECTORS ============
        f.write('\nLATTICE_CONSTANT\n')
        f.write(f"{stru['lat']['const']}\n")

        if 'vec' in stru['lat']:
            f.write('\nLATTICE_VECTORS\n')
            for v in stru['lat']['vec']:
                f.write(f'{v[0]} {v[1]} {v[2]}\n')

        if 'param' in stru['lat']:
            f.write('\nLATTICE_PARAMETER\n')
            for param in stru['lat']['param']:
                f.write(f'{param} ')
            f.write('\n')

        #============ ATOMIC_POSITIONS ============
        f.write('\nATOMIC_POSITIONS\n')
        f.write(f"{stru['coord_type']}\n")

        for s in stru['species']:
            f.write(f"\n{s['symbol']}\n")
            f.write(f"{s['mag_each']}\n")
            f.write(f"{s['natom']}\n")

            for atom in s['atom']:
                f.write(' '.join(f'{x}' for x in atom['coord']))

                for key in ['m', 'v']: # frozen atom / initial velocity
                    if key in atom:
                        f.write(f' {key}' +
                                ''.join(f' {x}' for x in atom[key]))

                if 'mag' in atom:
                    if not isinstance(atom['mag'], tuple): # collinear
                        f.write(f" mag {atom['mag']}")
                    else: # non-collinear
                        mag_coord_type, mag = atom['mag']
                        assert mag_coord_type in ['Cartesian', 'Spherical']
                        if mag_coord_type == 'Cartesian':
                            f.write(f' mag {mag[0]} {mag[1]} {mag[2]}')
                        else:
                            f.write(f' mag {mag[0]} angle1 {mag[1]} angle2 {mag[2]}')

                f.write('\n')


def species_group_indices(symbols: List[str]) -> List[int]:
    """Return indices grouped by first-occurrence species order."""
    species_order = list(dict.fromkeys(symbols))
    return [i for species in species_order for i, symbol in enumerate(symbols) if symbol == species]


def _constraint_mobility(atoms: Atoms) -> np.ndarray:
    """Return ABACUS mobility flags derived from ASE constraints."""
    mobility = np.ones((len(atoms), 3), dtype=int)
    for constraint in atoms.constraints:
        if isinstance(constraint, FixAtoms):
            mobility[constraint.get_indices()] = 0
        elif isinstance(constraint, FixCartesian):
            indices = np.asarray(constraint.get_indices(), dtype=int)
            mask = np.asarray(constraint.mask, dtype=bool)
            if mask.ndim == 1:
                mobility[np.ix_(indices, np.where(mask)[0])] = 0
            else:
                for atom_index, atom_mask in zip(indices, mask):
                    mobility[atom_index, atom_mask] = 0
    return mobility


def write_stru(stru: Atoms,
               outdir: str,
               pp_file: Optional[Dict[str, str]],
               orb_file: Optional[Dict[str, str]] = None,
               fname: Optional[str] = 'STRU') -> str:
    '''
    write the ABACUS STRU file from an Atoms object into outdir.

    Parameters
    ----------
    stru : Atoms
        The Atoms object to write.
    outdir : str
        The directory to write the STRU file.
    pp_file : dict
        A dictionary mapping element symbols to pseudopotential file names.
        The keys are the element symbols, and the values are the paths to
        the pseudopotential files.
    orb_file : dict, optional
        A dictionary mapping element symbols to orbital file names.
        The keys are the element symbols, and the values are the paths to
        the orbital files. If None, no orbital files will be written.
    fname : str, optional
        The name of the STRU file to write. Default is 'STRU'.

    Returns
    -------
    str
        The path to the written STRU file.
    '''
    from ase.units import (
        Bohr as __BOHR__,
        Angstrom as __ANGSTROM__
    )
    assert isinstance(stru, Atoms)
    pp_file = pp_file or {} # can be None, for those non-ESolver_KS cases

    elem = stru.get_chemical_symbols()
    # ABACUS requires the atoms ranged species-by-species, therefore
    # we need to group atoms by species. Preserve first-occurrence species
    # order from ASE instead of forcing alphabetical order.
    ind = species_group_indices(elem)
    coords = stru.get_positions()[ind]
    mobility = _constraint_mobility(stru)[ind]
    elem = [elem[i] for i in ind]

    # handle the atomic magnetic moment (issue #6516)
    magmoms = np.array([stru[i].magmom for i in ind]).reshape(len(stru), -1) # ncol in [1, 3]
    magmoms = [{} if abs(np.linalg.norm(m)) <= 1e-10
               else {'mag': m[0] if len(m) == 1 else ('Cartesian', m.tolist())}
               for m in magmoms]
    elem_uniq = list(dict.fromkeys(elem))
    nat = np.array([elem.count(e) for e in elem_uniq])
    stru_dict = {
        'coord_type': 'Cartesian',
        'lat': {
            'const': __ANGSTROM__ / __BOHR__,
            'vec': np.array(stru.get_cell()).tolist()
        },
        'species': [
            {
                'symbol': e,
                'mass': ATOM_MASS[e],
                'pp_file': pp_file.get(e, ''),
                'pp_type': '',
                'natom': n,
                'mag_each': 0.0,
                'atom': [
                    magmoms[j] | {
                        'coord': coords[j].tolist(), # coordinate
                        'm': mobility[j].tolist(), # mobility
                        'v': [0.0, 0.0, 0.0], # velocity
                    } for j in range(np.sum(nat[:i]), np.sum(nat[:i+1]))
                ]
            }
            for i, (n, e) in enumerate(zip(nat, elem_uniq))
        ]
    }
    if orb_file is not None:
        for s in stru_dict['species']:
            s['orb_file'] = orb_file[s['symbol']]

    _write_stru(outdir, stru_dict, fname)

    return (Path(outdir) / fname).resolve().as_posix()
