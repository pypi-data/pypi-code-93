import numpy as np


def element_stiffness_matrix(element) -> np.array:
    """
    element stiffness matrix
    [fx1,fy1,fx2,fy2]' = k*[dx1,dy1,dx2,dy2]'
    """
    E = element.cross_section.E
    A = element.cross_section.A
    l = element.length
    dx = element.node2.x - element.node1.x
    dy = element.node2.y - element.node1.y
    c2 = (dx / l) ** 2
    s2 = (dy / l) ** 2
    cs = (dx * dy) / l ** 2
    k = (
        np.array(
            [
                [c2, cs, -c2, -cs],
                [cs, s2, -cs, -s2],
                [-c2, -cs, c2, cs],
                [-cs, -s2, cs, s2],
            ]
        )
        * (E * A)
        / l
    )
    return k


def global_stiffness_matrix(model) -> np.array:
    K = np.zeros((model.ndofs, model.ndofs))
    for element in model.elements:
        ndof = element.ndof
        dofs = element.dofs
        kel = element_stiffness_matrix(element)
        for i in range(ndof):
            for j in range(ndof):
                K[dofs[i]][dofs[j]] += kel[i][j]
    return K


def element_forces(elements, global_deformations):
    element_forces = dict()
    for element in elements:
        deformations = global_deformations[element.dofs]
        E = element.cross_section.E
        A = element.cross_section.A
        l = element.length
        dx = element.node2.x - element.node1.x
        dy = element.node2.y - element.node1.y
        c = dx / l
        s = dy / l
        f = np.array([-c, -s, c, s]).dot(deformations) * (E * A) / l
        element_forces[element.id] = f
    return element_forces


def solve_linear_elastic(model):
    """
    K*d=f
    """
    K = global_stiffness_matrix(model)
    K0 = K.copy()
    f = model.load_vector()
    d = np.zeros((model.ndofs))
    supp_dofs = model.supported_dofs()
    no_supp_dofs = [i for i in range(model.ndofs) if i not in supp_dofs]
    K = np.delete(K, supp_dofs, 0)
    K = np.delete(K, supp_dofs, 1)
    f = np.delete(f, supp_dofs)
    d_no_supp = np.linalg.solve(K, f)
    for no_supp_dof, d1 in zip(no_supp_dofs, d_no_supp):
        d[no_supp_dof] = d1
    return d, element_forces(model.elements, d)
