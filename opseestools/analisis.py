# -*- coding: utf-8 -*-

from openseespy.opensees import *
import matplotlib.pyplot as plt
import numpy as np
import opseestools.utilidades as ut

# ANALISIS DE GRAVEDAD
# =============================
def gravedad():
    '''
    Function to perform an static analysis

    Returns
    -------
    None.

    '''
    
# Create the system of equation, a sparse solver with partial pivoting
    system('BandGeneral')

# Create the constraint handler, the transformation method
    constraints('Plain')

# Create the DOF numberer, the reverse Cuthill-McKee algorithm
    numberer('RCM')

# Create the convergence test, the norm of the residual with a tolerance of
# 1e-12 and a max number of iterations of 10
    test('NormDispIncr', 1.0e-12, 10, 3)

# Create the solution algorithm, a Newton-Raphson algorithm
    algorithm('Newton')

# Create the integration scheme, the LoadControl scheme using steps of 0.1
    integrator('LoadControl', 0.1)

# Create the analysis object
    analysis('Static')

    ok = analyze(10)
    
    # if ok != 0:
    #     print('Análisis de gravedad fallido')
    #     sys.exit()
    # else:
    #     print('Análisis de gravedad completado')
        


# ANALISIS PUSHOVER
# =============================

def pushover(Dmax,Dincr,IDctrlNode,IDctrlDOF):
    '''
    Basic function to perform a pushover analysis. Lacks powerful convergence algorithms.

    Parameters
    ----------
    Dmax : float
        target displacement.
    Dincr : float
        displacement increment.
    IDctrlNode : integer
        tag with the node for increment control.
    IDctrlDOF : integer
        DOF of the pushover. Use 1 for x direction.

    Returns
    -------
    returns a file named techo.out with the pushover results.

    '''
    
    recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 6
    Tol = 1e-8
      
    
    wipeAnalysis()
    constraints('Transformation')
    numberer('Plain')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')
    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    
    Nsteps =  int(Dmax/ Dincr)
    
    ok = analyze(Nsteps)
    print(ok)
    print('Pushover completado sin problemas')
    
    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}
    
    
    for i in tests:
        for j in algoritmo:
    
            if ok != 0:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
                    
                else:
                    algorithm(algoritmo[j])
                    
                test(tests[i], Tol, 1000)
                ok = analyze(Nsteps)                            
                print(tests[i], algoritmo[j], ok)             
                if ok == 0:
                    break
            else:
                continue
            
def pushover2(Dmax,Dincr,IDctrlNode,IDctrlDOF,norm=[-1,1],Tol=1e-8):
    '''
    Function to calculate the pushover

    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : numpy array
        Numpy array with the roof displacement recorded during the Pushover.
    V : numpy array
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier

    '''
    
    
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    
    # Eds = np.zeros((nels, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    return techo, V

#%% ================================ PUSHOVER CON REMOVAL =================================

def pushover2R(Dmax,Dincr,IDctrlNode,IDctrlDOF,ele,der,nodes_control,elements,norm=[-1,1],Tol=1e-8):
    '''
    Function that calculates the pushover, recording information about beams, columns and infills. Allows the removal of infills.

    Parameters
    ----------
    Dmax : TYPE
        Maximum displacement of the pushover..
    Dincr : TYPE
        Increment in the displacement..
    IDctrlNode : TYPE
        control node during the pushover.
    IDctrlDOF : TYPE
        DOF for the displacement.
    ele : TYPE
        tags of diagonal strut elements of the walls. Input them pair-wise for the walls, i.e., the two of each walls at the time..
    der : TYPE
        limit drift for each wall.
    nodes_control : TYPE
        control nodes to record information. Input one per floor in order to get inter-story drifts. Otherwise you will get an error..
    elements : TYPE
        element tags to record forces (columns and beams).
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        tolerance for the analysis. The default is 1e-8.

    Returns
    -------
    techo : TYPE
        Numpy array with the roof displacement recorded during the Pushover..
    V : TYPE
        Numpy array with the base shear (when using an unitary pattern) recorded during the Pushover. If pattern if not unitary it returns the multiplier.
    Eds : TYPE
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    f_puntalA : TYPE
        Numpy array with the forces in the struts (odds).
    f_puntalB : TYPE
        Numpy array with the forces in the struts (even).
    node_disp : TYPE
        Numpy array with displacements in the DOF specified in IDctrlDOF, of the nodes defined in the input variable nodes_control..
    drift : TYPE
        Numpy array with the interstory drif of each building story at each pushover instant. Columns are the nodes and rows are pushover instants..
    unicos2 : TYPE
        Numppy arrays that indicates the pushover instants where struts are present..

    '''
 
 
    maxNumIter = 10                                                             # Máximo número de iteraciones
    
    # ------------------- Configuración básica del análisis -------------------
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    # ----------------------- Otras opciones de análisis ----------------------   
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}
    # -------------------------- Rutina del análisis --------------------------
    
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    dmuro1 = [nodeDisp(1001,IDctrlDOF)]
    dmuro2 = [nodeDisp(1002,IDctrlDOF)]
    Vbasal = [getTime()]
    
    nels = len(elements)
    Eds = np.zeros((nels, Nsteps+1, 6)) 
                                   
    
    nnodos = len(nodes_control)
    f_puntalB = np.zeros((len(ele),Nsteps,6))
    f_puntalA = np.zeros((len(ele),Nsteps,6))
    flag = np.zeros((len(ele),Nsteps))
    node_disp = np.zeros((Nsteps + 1, nnodos))                                  # Para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1))                                  # Para grabar la deriva de entrepiso
    
    kfails = 1e9*np.ones(len(ele))                                              # Para identificar el punto donde el muro "falla" (tiempo)
        
    nodeI=[]
    nodeJ=[]
    for n in range(len(ele)):
        nodes= eleNodes(ele[n][1])
        nodeI.append(nodes[0])
        nodeJ.append(nodes[1])
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
        for i in range(len(ele)):
            f1,a,flag1 = removalTH2(nodeI[i],nodeJ[i],ele[i],der[i])
            f_puntalA[i,k,:] = f1
            f_puntalB[i,k,:] = a
            if flag1 == 1:
                kfails[i] = np.min((k,kfails[i]))
                
        for el_i, ele_tag in enumerate(elements):
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    unicos = np.unique(kfails)                                                  # Para encontrar los valores únicos donde se producen fallas de la mamposteria
    unicos2 = unicos[unicos<1e8]                                                # Para quitar los valores de 1e9 que hicimos para el artificio
    
    return techo, V, Eds, f_puntalA, f_puntalB, node_disp, drift, unicos2

#%%Pushover con removal, considernado rotaciones y deformaciones unitarias 
#En este es importante cambiar las fibras en donde se quiere guardar registro
def pushover2R_Rot_def(Dmax,Dincr,IDctrlNode,IDctrlDOF,columns,beams,ele,der,nodes_control,elements,id_s,id_c,norm=[-1,1],Tol=1e-8):
    '''
    Performs a pushover extracting rotations, element forces, drift ratios, node displacements.

    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    columns : list
        List with the column tags to record information. Information will be recorded in the same order as input.
    beams : list
        List with the beam tags to record information. Information will be recorded in the same order as input..
    ele : list
        tags of diagonal strut elements of the walls. Input them pair-wise for the walls, i.e., the two of each walls at the time.
    der : float
        limit drift for each wall
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error..
    elements : list
        beam and column elements in one single list.
    id_s : int
        ID of the steel material.
    id_c : int
        ID of the concrete material.
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : float
        Numpy array with the roof displacement recorded during the Pushover..
    V : float
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier.
    Eds : float
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    f_puntalA : float
        Numpy array with the forces in the struts (odds).
    f_puntalB : float
        Numpy array with the forces in the struts (even).
    node_disp : float
        Numpy array with displacements in the DOF specified in IDctrlDOF, of the nodes defined in the input variable nodes_control..
    drift : float
        Numpy array with the interstory drif of each building story at each pushover instant. Columns are the nodes and rows are pushover instants..
    unicos2 : float
        Numppy arrays that indicates the pushover instants where struts are present..
    Prot_cols : float
        Numpy array with the rotation at the columns specified in columns.
    Prot_beams : float
        Numpy array with the rotation at the columns specified in columns.
    fiber_s : float
        Numpy array with the stress at steel at the columns specified in columns.
    fiber_c : float
        Numpy array with the stress at steel at the columns specified in columns.


    
    '''
     
    maxNumIter = 10                                                             # Máximo número de iteraciones
    
    # ------------------- Configuración básica del análisis -------------------
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    # ----------------------- Otras opciones de análisis ----------------------   
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}
    # -------------------------- Rutina del análisis --------------------------
    
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    dmuro1 = [nodeDisp(1001,IDctrlDOF)]
    dmuro2 = [nodeDisp(1002,IDctrlDOF)]
    Vbasal = [getTime()]
    
    nels = len(elements)
    ncols = len(columns)
    nbeams = len(beams)
    Eds = np.zeros((nels, Nsteps+1, 6)) 
    Prot_cols = np.zeros((ncols, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    Prot_beams = np.zeros((nbeams, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    fiber_c = np.zeros((ncols, Nsteps+1, 2)) 
    fiber_s = np.zeros((ncols, Nsteps+1, 2)) 
    
    nnodos = len(nodes_control)
    f_puntalB = np.zeros((len(ele),Nsteps,6))
    f_puntalA = np.zeros((len(ele),Nsteps,6))
    flag = np.zeros((len(ele),Nsteps))
    node_disp = np.zeros((Nsteps + 1, nnodos))                                  # Para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1))                                  # Para grabar la deriva de entrepiso
    
    kfails = 1e9*np.ones(len(ele))                                              # Para identificar el punto donde el muro "falla" (tiempo)
        
    nodeI=[]
    nodeJ=[]
    for n in range(len(ele)):
        nodes= eleNodes(ele[n][1])
        nodeI.append(nodes[0])
        nodeJ.append(nodes[1])
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
        for i in range(len(ele)):
            f1,a,flag1 = removalTH2(nodeI[i],nodeJ[i],ele[i],der[i])
            f_puntalA[i,k,:] = f1
            f_puntalB[i,k,:] = a
            if flag1 == 1:
                kfails[i] = np.min((k,kfails[i]))
                
        for el_i, ele_tag in enumerate(elements):
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
        for el_i, col_tag in enumerate(columns):
           
           fiber_s[el_i , k+1, :] = eleResponse(col_tag,'section',1,'fiber',0.19,0.0,id_s,'stressStrain')
           fiber_c[el_i , k+1, :] = eleResponse(col_tag,'section',1,'fiber',-0.23,0.0,id_c,'stressStrain')
        
           Prot_cols[el_i , k+1, :] = [eleResponse(col_tag,'plasticDeformation')[0],
                                eleResponse(col_tag,'plasticDeformation')[1],
                                eleResponse(col_tag,'plasticDeformation')[2]]
           
        for el_i, b_tag in enumerate(beams):
        
           Prot_beams[el_i , k+1, :] = [eleResponse(b_tag,'plasticDeformation')[0],
                                eleResponse(b_tag,'plasticDeformation')[1],
                                eleResponse(b_tag,'plasticDeformation')[2]]
           
           
            
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    unicos = np.unique(kfails)                                                  # Para encontrar los valores únicos donde se producen fallas de la mamposteria
    unicos2 = unicos[unicos<1e8]                                                # Para quitar los valores de 1e9 que hicimos para el artificio
    
    return techo, V, Eds, f_puntalA, f_puntalB, node_disp, drift, unicos2, Prot_cols,Prot_beams, fiber_s, fiber_c


def pushover2Rot(Dmax,Dincr,IDctrlNode,IDctrlDOF,elements,norm=[-1,1],Tol=1e-8,forces=False):
    
    '''
    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        beam and column elements in one single list to record rotations.

    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : float
        Numpy array with the roof displacement recorded during the Pushover..
    V : float
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier.   
    PRot : float
        Numpy array with the rotation at the specified elements.
    
    '''
    
    
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    nels = len(elements)
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    Prot = np.zeros((nels, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    Eds = np.zeros((nels, Nsteps+1, 6)) 
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for el_i, ele_tag in enumerate(elements):
            
            Prot[el_i , k+1, :] = [eleResponse(ele_tag,'plasticDeformation')[0],
                                  eleResponse(ele_tag,'plasticDeformation')[1],
                                  eleResponse(ele_tag,'plasticDeformation')[2]]
            if forces != False:
                Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                     eleResponse(ele_tag,'globalForce')[1],
                                     eleResponse(ele_tag,'globalForce')[2],
                                     eleResponse(ele_tag,'globalForce')[3],
                                     eleResponse(ele_tag,'globalForce')[4],
                                     eleResponse(ele_tag,'globalForce')[5]]
            
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    if forces != False:
        return techo, V, Prot,Eds
    else:
        return techo, V, Prot

def pushover2D(Dmax,Dincr,IDctrlNode,IDctrlDOF,nodes_control,norm=[-1,1],Tol=1e-8):
    '''
    Performs a pushover analysis extracting the inter-story drifts
    
    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : float
        Numpy array with the roof displacement recorded during the Pushover..
    V : float
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier.
    drift : float
        Numpy array with the interstory drif of each building story at each pushover instant. Columns are the nodes and rows are pushover instants..
   
        
    '''
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
         
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    nnodos = len(nodes_control)
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
      
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    return techo, V, drift


def pushover2C(displ,Dincr,IDctrlNode,IDctrlDOF,norm=[-1,1],Tol=1e-4):
    '''
    Performs a cyclic pushover analysis of the structure.

    Parameters
    ----------
    displ : list
        List with the peak displacement of the cycles of the pushover.
    Dincr : float
        Displacement increment.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : float
        Numpy array with the roof displacement recorded during the Pushover..
    V : float
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier.

    '''

    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('NormUnbalance', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    currdisp = 0 # LINEA NUEVA
    for dis in displ: # LINEA NUEVA
        Nsteps =  int(np.abs(dis - currdisp) / Dincr) # LINEA NUEVA PORQUE TOCO EDITAR LA OTRA
        if dis > 0: # LINEA NUEVA
            integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr) # LINEA NUEVA
        else: # LINEA NUEVA
            integrator('DisplacementControl', IDctrlNode, IDctrlDOF, -Dincr) # LINEA NUEVA
        for k in range(Nsteps):
            ok = analyze(1)
            # ok2 = ok;
            # En caso de no converger en un paso entra al condicional que sigue
            if ok != 0:
                print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
                for j in algoritmo:
                    if j < 4:
                        algorithm(algoritmo[j], '-initial')
        
                    else:
                        algorithm(algoritmo[j])
                    
                    # el test se hace 50 veces más
                    test('NormUnbalance', Tol, maxNumIter*50)
                    ok = analyze(1)
                    if ok == 0:
                        # si converge vuelve a las opciones iniciales de análisi
                        test('NormUnbalance', Tol, maxNumIter)
                        algorithm('Newton')
                        break
                        
            if ok != 0:
                print('Pushover analisis fallido')
                print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
                break
        
            
            dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
            Vbasal.append(getTime())
        currdisp = nodeDisp(IDctrlNode,IDctrlDOF) # LINEA NUEVA
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    return techo, V

def pushover2MP(Dmax,Dincr,IDctrlNode,IDctrlDOF,norm=[-1,1],Tol=1e-8):
    
    # creación del recorder de techo y definición de la tolerancia
    recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 20
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*25)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
    
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        

    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    return techo, V


def pushover2T(Dmax,Dincr,IDctrlNode,IDctrlDOF,norm=[-1,1],Tol=1e-8):
    
    '''
    Function to calculate the pushover and the building period during this one.

    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : numpy array
        Numpy array with the roof displacement recorded during the Pushover.
    V : numpy array
        Numpy array with the base shear (when using an unitary pattern) recorded during the Pushover. If pattern is not unitary it returns the multiplier
    T : numpy array
        Numpy array with the building period recorded during the Pushover.
    '''
    
    
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    eig = eigen(1)
    TT = 2*3.1416/np.sqrt(eig[0])
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    periods = [TT]
    fibras1 = [0]*8
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
       
        eig = eigen(1)
        TT = 2*3.1416/np.sqrt(eig[0])
        periods.append(TT)
         
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    PER = np.array(periods)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    plt.figure()
    plt.plot(dtecho,periods)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('Periodo (s)')
    
    return techo, V, PER

def pushover3T(Dmax,Dincr,IDctrlNode,IDctrlDOF,elements,norm=[-1,1],Tol=1e-8):
    '''
    Function to calculate the pushover

    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : numpy array
        Numpy array with the roof displacement recorded during the Pushover.
    V : numpy array
        Numpy array with the base shear (when using an unitary pattern) recorded during the Pushover. If pattern is not unitary it returns the multiplier
    T : numpy array
        Numpy array with the building period recorded during the Pushover.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    Strains : 
        Strain at the macrofibers of the wall. Records eight.
    cStress : 
        Concrete stress at the macrofibers of the wall. Records eight.
    sStress :
        Steel stress at the macrofibers of the wall. Records eight.

    '''
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    eig = eigen(1)
    TT = 2*3.1416/np.sqrt(eig[0])
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    periods = [TT]
    
    
    nels = len(elements)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Curv = np.zeros((nels,Nsteps+1)) # para grabar la curvatura de los elementos
    # Strains = np.zeros((Nsteps+1, 8, nels)) # # para grabar las deformaciones de los muros en las 8 fibras que tienen los elementos
    Strains = np.zeros((nels, Nsteps+1, 8))
    cStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del concreto de los muros en las 8 fibras que tienen los elementos
    sStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del acero de los muros en las 8 fibras que tienen los elementos
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        
        for el_i, ele_tag in enumerate(elements):
            
            # Curv[k+1, el_i] = [eleResponse(ele_tag,'Curvature')]
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
            Strains[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Strain')[0],
                                 eleResponse(ele_tag,'Fiber_Strain')[1],
                                 eleResponse(ele_tag,'Fiber_Strain')[2],
                                 eleResponse(ele_tag,'Fiber_Strain')[3],
                                 eleResponse(ele_tag,'Fiber_Strain')[4],
                                 eleResponse(ele_tag,'Fiber_Strain')[5],
                                 eleResponse(ele_tag,'Fiber_Strain')[6],
                                 eleResponse(ele_tag,'Fiber_Strain')[7]]
            
            cStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Concrete')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[7]]
            
            sStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Steel')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[7]]
        
        eig = eigen(1)
        TT = 2*3.1416/np.sqrt(eig[0])
        periods.append(TT)
         
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    PER = np.array(periods)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    plt.figure()
    plt.plot(dtecho,periods)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('Periodo (s)')
    
    return techo, V, PER, Eds, Strains, cStress, sStress



def pushover3Tn(Dmax,Dincr,IDctrlNode,IDctrlDOF,elements,norm=[-1,1],Tol=1e-8):
    
    # creación del recorder de techo y definición de la tolerancia
    recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    eig = eigen(1)
    TT = 2*3.1416/np.sqrt(eig[0])
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    periods = [TT]
    
    
    nels = len(elements)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Curv = np.zeros((nels,Nsteps+1)) # para grabar la curvatura de los elementos
    # Strains = np.zeros((Nsteps+1, 8, nels)) # # para grabar las deformaciones de los muros en las 8 fibras que tienen los elementos
    Strains = np.zeros((nels, Nsteps+1, 14))
    cStress = np.zeros((nels, Nsteps+1, 14)) # # para grabar los esfuerzos del concreto de los muros en las 8 fibras que tienen los elementos
    sStress = np.zeros((nels, Nsteps+1, 14)) # # para grabar los esfuerzos del acero de los muros en las 8 fibras que tienen los elementos
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        
        for el_i, ele_tag in enumerate(elements):
            
            # Curv[k+1, el_i] = [eleResponse(ele_tag,'Curvature')]
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
            Strains[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Strain')[0],
                                 eleResponse(ele_tag,'Fiber_Strain')[1],
                                 eleResponse(ele_tag,'Fiber_Strain')[2],
                                 eleResponse(ele_tag,'Fiber_Strain')[3],
                                 eleResponse(ele_tag,'Fiber_Strain')[4],
                                 eleResponse(ele_tag,'Fiber_Strain')[5],
                                 eleResponse(ele_tag,'Fiber_Strain')[6],
                                 eleResponse(ele_tag,'Fiber_Strain')[7],
                                 eleResponse(ele_tag,'Fiber_Strain')[8],
                                 eleResponse(ele_tag,'Fiber_Strain')[9],
                                 eleResponse(ele_tag,'Fiber_Strain')[10],
                                 eleResponse(ele_tag,'Fiber_Strain')[11],
                                 eleResponse(ele_tag,'Fiber_Strain')[12],
                                 eleResponse(ele_tag,'Fiber_Strain')[13]]
                                 
            
            cStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Concrete')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[7],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[8],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[9],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[10],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[11],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[12],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[13]]
                                 
            
            sStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Steel')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[7],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[8],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[9],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[10],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[11],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[12],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[13]]


        eig = eigen(1)
        TT = 2*3.1416/np.sqrt(eig[0])
        periods.append(TT)
         
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    PER = np.array(periods)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    
    plt.figure()
    plt.plot(dtecho,periods)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('Periodo (s)')
    
    return techo, V, PER, Eds, Strains, cStress, sStress


# ANALISIS DINAMICO
# =============================   

# dinamico es el más sencillo de todos, corre un terremoto creando un recorder para el techo.
# dinamicoIDA crea el recorder en función del factor escalar.
# dinamicoAnim es dinamico pero guarda la información para animar el registro
# dinamicoIDA2 está modificado para ser utilizado cuando se desee correr en paralelo los cálculos. Devuelve solo el desplazamiento de techo
# dinamicoIDA3 PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS. SOLO PUEDEN SER LOS MUROS DE MOMENTO. También extrae desplazamientos de los nodos
# dinamicoIDA4 PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS. SOLO PUEDEN SER LOS MUROS DE MOMENTO. También extrae desplazamientos de los nodos, aceleraciones, derivas, velocidades, esfuerzos en concreto, acero y deformaciones unitarias de cada muro indicado en elements
# dinamicoIDA5 es lo mismo que IDA4, pero en lugar del nombre del registro, recibe una lista con las aceleraciones.

def dinamico(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,modes = [0,2],Kswitch = 1,Tol=1e-4):
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    # IDctrlNode,IDctrlDOF son respectivamente el nodo y desplazamiento de control deseados
    
    # creación del recorder de techo y definición de la tolerancia
    recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 25
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('NormDispIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('NormDispIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('NormDispIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
    
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')  
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    
    
    
    return tiempo,techo
     
def dinamicoIDA(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,modes = [0,2],Kswitch = 1,Tol=1e-4):
    '''

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    None.

    '''
    # modelName
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    # IDctrlNode,IDctrlDOF son respectivamente el nodo y desplazamiento de control deseados
     # creación del recorder de techo y definición de la tolerancia
    # nombre = str(int(fact/9.81*100))
    # recorder('Node','-file','techo'+nombre+'.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 25
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('NormDispIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('NormDispIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('NormDispIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
    
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    # techo = np.array(dtecho)
    # tiempo = np.array(t)
    wipe()
   
def dinamicoAnim(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,modes = [0,2],Kswitch = 1,Tol=1e-8):
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    # IDctrlNode,IDctrlDOF son respectivamente el nodo y desplazamiento de control deseados
    
    # creación del recorder de techo y definición de la tolerancia
    recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    el_tags = getEleTags()
    nels = len(el_tags)
    Eds = np.zeros((Nsteps+1, nels, 6))
    
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
    
        for el_i, ele_tag in enumerate(el_tags):
            nd1, nd2 = eleNodes(ele_tag)
            Eds[k+1, el_i, :] = [nodeDisp(nd1)[0],
                                  nodeDisp(nd1)[1],
                                  nodeDisp(nd1)[2],
                                  nodeDisp(nd2)[0],
                                  nodeDisp(nd2)[1],
                                  nodeDisp(nd2)[2]]
        
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    plt.figure()
    plt.plot(t,dtecho)
    plt.xlabel('tiempo (s)')
    plt.ylabel('desplazamiento (m)')  
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    
    return tiempo,techo,Eds
    
def dinamicoIDA2(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,modes = [0,2],Kswitch = 1,Tol=1e-8):
    '''
    Performs a dynamic analysis recording the displacement of a user selected node.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.

    '''
    
    
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
    
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    wipe()
    return tiempo,techo


def dinamicoIDA4(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-8):
    '''
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces, stresses and strain. To be used only with wall buildings modeled with the MVLEM.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.


    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    Strains : numpy array
        Strain at the macrofibers of the wall. Records eight.
    cStress : numpy array
        Concrete stress at the macrofibers of the wall. Records eight.
    sStress : numpy array
        Steel stress at the macrofibers of the wall. Records eight.
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.

    '''
    
    
    
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # IDcrtlNode es el nodo de control para grabar desplazamientos
    # IDctrlDOF es el grado de libertad de control
    # elements son los elementos de los que se va a grabar información
    # nodes_control son los nodos donde se va a grabar las respuestas
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    nnodos = len(nodes_control)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Curv = np.zeros((nels,Nsteps+1)) # para grabar la curvatura de los elementos
    
    Strains = np.zeros((nels, Nsteps+1, 8))
    cStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del concreto de los muros en las 8 fibras que tienen los elementos
    sStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del acero de los muros en las 8 fibras que tienen los elementos
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
                       

        for el_i, ele_tag in enumerate(elements):
            
            # Curv[k+1, el_i] = [eleResponse(ele_tag,'Curvature')]
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
            Strains[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Strain')[0],
                                 eleResponse(ele_tag,'Fiber_Strain')[1],
                                 eleResponse(ele_tag,'Fiber_Strain')[2],
                                 eleResponse(ele_tag,'Fiber_Strain')[3],
                                 eleResponse(ele_tag,'Fiber_Strain')[4],
                                 eleResponse(ele_tag,'Fiber_Strain')[5],
                                 eleResponse(ele_tag,'Fiber_Strain')[6],
                                 eleResponse(ele_tag,'Fiber_Strain')[7]]
            
            cStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Concrete')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[7]]
            
            sStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Steel')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[7]]
            
            
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    wipe()
    return tiempo,techo,Eds,Strains,cStress,sStress,node_disp,node_vel,node_acel,drift


def dinamicoIDA4T(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-8):
    
    '''
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces. Only allows elements with six DOF. Returns the period at the end of the analysis.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.
    Tf: float
        Period at the end of the analysis

    '''
    
    # IGUAL A dinamicoIDA4T
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # IDcrtlNode es el nodo de control para grabar desplazamientos
    # IDctrlDOF es el grado de libertad de control
    # elements son los elementos de los que se va a grabar información
    # nodes_control son los nodos donde se va a grabar las respuestas
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    # timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    nnodos = len(nodes_control)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    Tf2 = [2*np.pi/w1]
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
                       

        for el_i, ele_tag in enumerate(elements):
            
            # Curv[k+1, el_i] = [eleResponse(ele_tag,'Curvature')]
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        # eigvalF = eigen(nmodes)
        
        # eigF = eigvalF[modes[0]]
        
        # wF = eigF**0.5
        # Tf= 2*np.pi/wF
        # Tf2.append(Tf)
        
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    eigvalF = eigen(nmodes)
    
    eigF = eigvalF[modes[0]]
    
    wF = eigF**0.5
    Tf= 2*np.pi/wF
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    wipe()
    return tiempo,techo,Eds,node_disp,node_vel,node_acel,drift,Tf


def dinamicoIDA4P(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-4):
    '''
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces. Only allows elements with six DOF.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    Strains : numpy array
        Strain at the macrofibers of the wall. Records eight.
    cStress : numpy array
        Concrete stress at the macrofibers of the wall. Records eight.
    sStress : numpy array
        Steel stress at the macrofibers of the wall. Records eight.

    '''
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # IDcrtlNode es el nodo de control para grabar desplazamientos
    # IDctrlDOF es el grado de libertad de control
    # elements son los elementos de los que se va a grabar información
    # nodes_control son los nodos donde se va a grabar las respuestas
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('NormUnbalance', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    nnodos = len(nodes_control)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Prot = np.zeros((nels, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    
    
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('NormUnbalance', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('NormUnbalance', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
                       

        for el_i, ele_tag in enumerate(elements):
                      
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
        
            
            # Prot[el_i , k+1, :] = [eleResponse(ele_tag,'plasticDeformation')[0],
            #                       eleResponse(ele_tag,'plasticDeformation')[1],
            #                       eleResponse(ele_tag,'plasticDeformation')[2]]
            
            
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    wipe()
    return tiempo,techo,Eds,node_disp,node_vel,node_acel,drift




def dinamicoIDA5(acceleration,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-8):    
    '''
    
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces. Only allows elements with six DOF.

    Parameters
    ----------
    acceleration : array
        array with the acceleration. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.

    '''        
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-values',*acceleration,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    nnodos = len(nodes_control)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Curv = np.zeros((nels,Nsteps+1)) # para grabar la curvatura de los elementos
    
    Strains = np.zeros((nels, Nsteps+1, 8))
    cStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del concreto de los muros en las 8 fibras que tienen los elementos
    sStress = np.zeros((nels, Nsteps+1, 8)) # # para grabar los esfuerzos del acero de los muros en las 8 fibras que tienen los elementos
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
                       

        for el_i, ele_tag in enumerate(elements):
            
            # Curv[k+1, el_i] = [eleResponse(ele_tag,'Curvature')]
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
            
            Strains[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Strain')[0],
                                 eleResponse(ele_tag,'Fiber_Strain')[1],
                                 eleResponse(ele_tag,'Fiber_Strain')[2],
                                 eleResponse(ele_tag,'Fiber_Strain')[3],
                                 eleResponse(ele_tag,'Fiber_Strain')[4],
                                 eleResponse(ele_tag,'Fiber_Strain')[5],
                                 eleResponse(ele_tag,'Fiber_Strain')[6],
                                 eleResponse(ele_tag,'Fiber_Strain')[7]]
            
            cStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Concrete')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Concrete')[7]]
            
            sStress[el_i , k+1, :] = [eleResponse(ele_tag,'Fiber_Stress_Steel')[0],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[1],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[2],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[3],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[4],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[5],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[6],
                                 eleResponse(ele_tag,'Fiber_Stress_Steel')[7]]
            
            
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    wipe()
    return tiempo,techo,Eds,Strains,cStress,sStress,node_disp,node_vel,node_acel,drift

def dinamicoIDA2DB(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,modes = [0,2],Kswitch = 1,Tol=1e-3, odb = 1, odbtag = 1000):
    import opstool as opst
    '''  
    Performs a dynamic analysis recording the displacement of a user selected node.
    
    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.

    '''
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   IDctrlDOF,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Transformation')
    numberer('RCM')
    system('BandGeneral')
    test('NormUnbalance', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    
    if odb == 1:
        ODB = opst.post.CreateODB(odb_tag=odbtag)
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('NormUnbalance', Tol, maxNumIter*10)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('NormUnbalance', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        ODB.fetch_response_step()    
        
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    if odb == 1:
        ODB.save_response()
    wipe()
    return tiempo,techo

def pushover2DB(Dmax,Dincr,IDctrlNode,IDctrlDOF,norm=[-1,1],Tol=1e-8,odb = 1, odbtag = 1001):
    '''
    Function to calculate the pushover

    Parameters
    ----------
    Dmax : float
        Maximum displacement of the pushover.
    Dincr : float
        Increment in the displacement.
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    norm : list, optional
        List that includes the roof displacement and the building weight to normalize the pushover and display the roof drift vs V/W plot. The default is [-1,1].
    Tol : float, optional
        Norm tolerance. The default is 1e-8.

    Returns
    -------
    techo : numpy array
        Numpy array with the roof displacement recorded during the Pushover.
    V : numpy array
        Numpy array with the base shear (when using an unitary patter) recorded during the Pushover. If pattern if not unitary it returns the multiplier

    '''
    
    
    # creación del recorder de techo y definición de la tolerancia
    # recorder('Node','-file','techo.out','-time','-node',IDctrlNode,'-dof',IDctrlDOF,'disp')
    maxNumIter = 10
    import opstool as opst
      
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('DisplacementControl', IDctrlNode, IDctrlDOF, Dincr)
    analysis('Static')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    
    Nsteps =  int(Dmax/ Dincr) 
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    Vbasal = [getTime()]
    
    # Eds = np.zeros((nels, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    
    ODB = opst.post.CreateODB(odb_tag=odbtag)
    
    for k in range(Nsteps):
        ok = analyze(1)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Pushover analisis fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        ODB.fetch_response_step()
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        Vbasal.append(getTime())
        
    plt.figure()
    plt.plot(dtecho,Vbasal)
    plt.xlabel('desplazamiento de techo (m)')
    plt.ylabel('corte basal (kN)')
    
    techo = np.array(dtecho)
    V = np.array(Vbasal)
    
    
    if norm[0] != -1:
        deriva = techo/norm[0]*100
        VW = V/norm[1]
        plt.figure()
        plt.plot(deriva,VW)
        plt.xlabel('Deriva de techo (%)')
        plt.ylabel('V/W')
    ODB.save_response()
    return techo, V

def dinamicoIDA4PResidual(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-4):
    '''
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces. Only allows elements with six DOF.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.
    Eds :
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
       
    residual_drift : numpy array  
        Residual drift at each story of the building, extracted from the last 2 seconds of free vibration. 
        
    node_acel_abs : numpy array  
        Absolute acceleration at each node in nodes_control. 
        

    '''
    # PARA SER UTILIZADO PARA CORRER EN PARALELO LOS SISMOS Y EXTRAYENDO LAS FUERZAS DE LOS ELEMENTOS INDICADOS EN ELEMENTS
    
    # record es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # IDcrtlNode es el nodo de control para grabar desplazamientos
    # IDctrlDOF es el grado de libertad de control
    # elements son los elementos de los que se va a grabar información
    # nodes_control son los nodos donde se va a grabar las respuestas
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    
    maxNumIter = 10
    
    # creación del pattern
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)
    
    # damping
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
    
    # configuración básica del análisis
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('NormUnbalance', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # Otras opciones de análisis    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # rutina del análisis
    Nsteps_extra = int(2.0 / dtan)    #Numero de pasos extra para deriva residual (2 segundos)
    Nsteps =  int(dtrec*nPts/dtan)+Nsteps_extra
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    nnodos = len(nodes_control)
    Eds = np.zeros((nels, Nsteps+1, 6)) # para grabar las fuerzas de los elementos
    Prot = np.zeros((nels, Nsteps+1, 3)) # para grabar las rotaciones de los elementos
    
    
    node_disp = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos)) # para grabar los desplazamientos de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1)) # para grabar la deriva de entrepiso
    residual_drift = np.zeros(( 1, nnodos - 1)) # para grabar la deriva residual de entrepiso
    node_acel_abs = np.zeros((Nsteps + 1, nnodos)) # para grabar las aceleraciones absolutas de los nodos
    accg = np.zeros((Nsteps + 1, nnodos))  #para grabar las aceleraciones del suelo
    
    
    acc = np.loadtxt(recordName)  #Carga las aceleraciones de cada registro
       
    if len(acc) < Nsteps:
        acc = np.pad(acc, (0, Nsteps - len(acc)), mode='constant') #Llena de ceross el registro hasta los 2 segundos adicioanles del residual
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en tiempo: ',getTime())
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('NormUnbalance', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('NormUnbalance', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            accg[k+1,node_i]= acc[k] * 9.81
            
                        
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
        
        

        for el_i, ele_tag in enumerate(elements):
                      
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]
        
        
            
        
            
            # Prot[el_i , k+1, :] = [eleResponse(ele_tag,'plasticDeformation')[0],
            #                       eleResponse(ele_tag,'plasticDeformation')[1],
            #                       eleResponse(ele_tag,'plasticDeformation')[2]]
            
            
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
        
    # plt.figure()
    # plt.plot(t,dtecho)
    # plt.xlabel('tiempo (s)')
    # plt.ylabel('desplazamiento (m)')
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    
    for node_i, node_tag in enumerate(nodes_control):
        residual_drift[0,node_i-1]=ut.residual_disp(drift[:,node_i-1], Nsteps-Nsteps_extra)  #Se calcula deriva residual usando la funcion de Utilidades
    
    node_acel_abs= node_acel +  accg   #Calcula la aceleracion absoluta como la suma de la relativa y la del suelo
    
    wipe()
    return tiempo,techo,Eds,node_disp,node_vel,node_acel,drift,residual_drift,node_acel_abs


#%% ========================== DINÁMICO CON REMOVAL ===========================
def dinamicoIDA4R(recordName,dtrec,nPts,dtan,fact,damp,IDctrlNode,IDctrlDOF,columns, beams, ele,der,elements,nodes_control,modes = [0,2],Kswitch = 1,Tol=1e-4):
    '''
    Performs a dynamic analysis for a ground motion, recording information about displacements, velocity, accelerations, forces. Only allows elements with six DOF.

    Parameters
    ----------
    recordName : string
        Name of the record including file extension (i.e., 'GM01.txt'). It must have one record instant per line. 
    dtrec : float
        time increment of the record.
    nPts : integer
        number of points of the record.
    dtan : float
        time increment to be used in the analysis. If smaller than dtrec, OpenSeesPy interpolates.
    fact : float
        scale factor to apply to the record.
    damp : float
        Damping percentage in decimal (i.e., use 0.03 for 3%).
    IDctrlNode : int
        control node for the displacements.
    IDctrlDOF : int
        DOF for the displacement.
    columns : list
        List with the column tags to record information. Information will be recorded in the same order as input.
    beams : list
        List with the beam tags to record information. Information will be recorded in the same order as input..
    ele : list
        tags of diagonal strut elements of the walls. Input them pair-wise for the walls, i.e., the two of each walls at the time.
    der : float
        limit drift for each wall
    elements : list
        elements to record forces and stresses.
    nodes_control : list
        nodes to compute displacements and inter-story drift. You must input one per floor, otherwise you'll get an error.
    modes : list, optional
        Modes of the structure to apply the Rayleigh damping. The default is [0,2] which uses the first and third mode.
    Kswitch : int, optional
        Use it to define which stiffness matrix should be used for the ramping. The default is 1 that uses initial stiffness. Input 2 for current stifness.
    Tol : float, optional
        Tolerance for the analysis. The default is 1e-4 because it uses the NormUnbalance test.

    Returns
    -------
    tiempo : numpy array
        Numpy array with analysis time.
    techo : numpy array
        Displacement of the control node.
    Eds : numpy array
        Numpy array with the forces in the elements (columns and beams). The order is determined by the order used in the input variable elements. The array has three dimensions. The first one is the element, the second one the pushover instant and the third one is the DOF.
    f_puntalA : numpy array
        Numpy array with the forces in the struts (odds).
    f_puntalB : numpy array
        Numpy array with the forces in the struts (even).
    node_disp : numpy array
        Displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_vel : numpy array
        Velocity at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    node_acel : numpy array
        Relative displacement at each node in nodes_control. Each column correspond to a node and each row to an analysis instant.
    drift : numpy array
        Drift at story of the building. Each column correspond to a node and each row to an analysis instant.

    '''
    
    
    # recordName es el nombre del registro, incluyendo extensión. P.ej. GM01.txt
    # dtrec es el dt del registro
    # nPts es el número de puntos del análisis (residual=nPts agergarle 2 seg dividos por el dt del registro)
    # dtan es el dt del análisis
    # fact es el factor escalar del registro
    # damp es el porcentaje de amortiguamiento (EN DECIMAL. p.ej: 0.03 para 3%)
    # Kswitch recibe: 1: matriz inicial, 2: matriz actual
    # IDctrlNode,IDctrlDOF son respectivamente el nodo y desplazamiento de control deseados
    # columns es el tag de las columnas
    # beams es el tag de las vigas
    # ele es el tag de los puntales que definen el muro
    # der es la deriva en la que el muro falla y se rompe
    # ** elements son los elementos a los que se les calcula la fuerza **
    # nodes_control son los nodos de control
    
    maxNumIter = 10
    bandera = [0]*len(ele)
    
    # ------------------------- Creación del pattern --------------------------
    
    timeSeries('Path',1000,'-filePath',recordName,'-dt',dtrec,'-factor',fact)
    pattern('UniformExcitation',  1000,   1,  '-accel', 1000)

    # -------------------------------- Damping --------------------------------
    # Kswitch = 1 calcula amortiguamiento proporcional a la rigidez inicial, si no es 1 lo calcula 
    # proporcional a la rigidez tangencial
    nmodes = max(modes)+1
    eigval = eigen(nmodes)
    eig1 = eigval[modes[0]]
    eig2 = eigval[modes[1]]
    w1 = eig1**0.5
    w2 = eig2**0.5
    
    beta = 2.0*damp/(w1 + w2)
    alfa = 2.0*damp*w1*w2/(w1 + w2)
    
    if Kswitch == 1:
        rayleigh(alfa, 0.0, beta, 0.0)
    else:
        rayleigh(alfa, beta, 0.0, 0.0)
        
    # ------------------- Configuración básica del análisis -------------------
    
    wipeAnalysis()
    constraints('Plain')
    numberer('RCM')
    system('BandGeneral')
    test('EnergyIncr', Tol, maxNumIter)
    algorithm('Newton')    
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    
    # ---------------------- Otras opciones de análisis -----------------------
    
    tests = {1:'NormDispIncr', 2: 'RelativeEnergyIncr', 4: 'RelativeNormUnbalance',5: 'RelativeNormDispIncr', 6: 'NormUnbalance'}
    algoritmo = {1:'KrylovNewton', 2: 'SecantNewton' , 4: 'RaphsonNewton',5: 'PeriodicNewton', 6: 'BFGS', 7: 'Broyden', 8: 'NewtonLineSearch'}

    # -------------------------- Rutina del análisis --------------------------
    
    Nsteps =  int(dtrec*nPts/dtan)
    dtecho = [nodeDisp(IDctrlNode,IDctrlDOF)]
    t = [getTime()]
    nels = len(elements)
    ncol = len(columns)
    nnodos = len(nodes_control)
    f_puntalA = np.zeros((len(ele),Nsteps,6))                                   # Para grabar fuerzas en el puntal A
    f_puntalB = np.zeros((len(ele),Nsteps,6))                                   # Para grabar fuerzas en el puntal B
    Eds = np.zeros((nels, Nsteps+1, 6))                                         # Para grabar las fuerzas de los elementos
 
    node_disp = np.zeros((Nsteps + 1, nnodos))                                  # Para grabar los desplazamientos de los nodos
    node_vel = np.zeros((Nsteps + 1, nnodos))                                   # Para grabar la velocidad de los nodos
    node_acel = np.zeros((Nsteps + 1, nnodos))                                  # Para grabar la aceleración de los nodos
    drift = np.zeros((Nsteps + 1, nnodos - 1))                                  # Para grabar la deriva de entrepiso
    
    kfails = 1e9*np.ones(len(ele))                                              # Para identificar el punto donde hay fallas
  
    nodeI=[]
    nodeJ=[]
    for n in range(len(ele)):
        nodes= eleNodes(ele[n][1])
        nodeI.append(nodes[0])
        nodeJ.append(nodes[1])
    
    for k in range(Nsteps):
        ok = analyze(1,dtan)
        # ok2 = ok;
        # En caso de no converger en un paso entra al condicional que sigue
        if ok != 0:
            print('configuración por defecto no converge en desplazamiento: ',nodeDisp(IDctrlNode,IDctrlDOF))
            for j in algoritmo:
                if j < 4:
                    algorithm(algoritmo[j], '-initial')
    
                else:
                    algorithm(algoritmo[j])
                
                # el test se hace 50 veces más
                test('EnergyIncr', Tol, maxNumIter*50)
                ok = analyze(1,dtan)
                if ok == 0:
                    # si converge vuelve a las opciones iniciales de análisi
                    test('EnergyIncr', Tol, maxNumIter)
                    algorithm('Newton')
                    break
                    
        if ok != 0:
            print('Análisis dinámico fallido')
            print('Desplazamiento alcanzado: ',nodeDisp(IDctrlNode,IDctrlDOF),'m')
            break
        
        for node_i, node_tag in enumerate(nodes_control):
            
            node_disp[k+1,node_i] = nodeDisp(node_tag,1)
            node_vel[k+1,node_i] = nodeVel(node_tag,1)
            node_acel[k+1,node_i] = nodeAccel(node_tag,1)
            if node_i != 0:
                drift[k+1,node_i-1] = (nodeDisp(node_tag,1) - nodeDisp(nodes_control[node_i-1],1))/(nodeCoord(node_tag,2) - nodeCoord(nodes_control[node_i-1],2))
        
        for el_i, ele_tag in enumerate(elements):
            
            Eds[el_i , k+1, :] = [eleResponse(ele_tag,'globalForce')[0],
                                 eleResponse(ele_tag,'globalForce')[1],
                                 eleResponse(ele_tag,'globalForce')[2],
                                 eleResponse(ele_tag,'globalForce')[3],
                                 eleResponse(ele_tag,'globalForce')[4],
                                 eleResponse(ele_tag,'globalForce')[5]]

            
        for i in range(len(ele)):
            if bandera[i] != 1:
                f1,a,flag1 = removalTH2(nodeI[i],nodeJ[i],ele[i],der[i])
                f_puntalA[i,k,:] = f1
                f_puntalB[i,k,:] = a
                bandera[i] = flag1
                if flag1 == 1:
                    kfails[i] = np.min((k,kfails[i]))
            else:
                f_puntalA[i,k,:] = [0]*6
                f_puntalB[i,k,:] = [0]*6
                # print('muerto el primero')
                if flag1 == 1:
                    kfails[i] = np.min((k,kfails[i]))
            
        dtecho.append(nodeDisp(IDctrlNode,IDctrlDOF))
        t.append(getTime())
    
    
    techo = np.array(dtecho)
    tiempo = np.array(t)
    
    unicos = np.unique(kfails)                                                  # Para encontrar los valores únicos donde se producen fallas de la mamposteria
    unicos2 = unicos[unicos<1e8]                                                # Para quitar los valores de 1e9 que hicimos para el artificio
    
    # retornar tiempo, desplazamiento de recho, Fuerzas globales,fuerza en el 
    # puntal A, fuerza en el puntal B, Desplazamiento, velocidad, aceleración, 
    # deriva, instante de tiempo en el que el muro falla
    
    return tiempo,techo,Eds,f_puntalA,f_puntalB,node_disp,node_vel,node_acel,drift,unicos2

#%% ============================ FUNCIONES REMOVAL ============================

def removal(nodeI,nodeJ,ele,der):
    fuerza=0
    d1= nodeDisp(nodeI,1)
    d2= nodeDisp(nodeJ,1)
    y1= nodeCoord(nodeI)[1]
    y2= nodeCoord(nodeJ)[1]
    deriva= (d2-d1)/(y2-y1)
    if abs(deriva) > der:
        remove('ele',ele)
    else:
        fuerza = eleForce(ele,1)
    return fuerza

def removalTH(nodeI,nodeJ,ele,der):
    fuerza = 0
    flag = 0
    d1= nodeDisp(nodeI,1)
    d2= nodeDisp(nodeJ,1)
    y1= nodeCoord(nodeI)[1]
    y2= nodeCoord(nodeJ)[1]
    deriva= (d2-d1)/(y2-y1)
    if abs(deriva) > der:
        remove('ele',ele)
        flag = 1
    else:
        fuerzax = eleForce(ele,1,2,3)
       
    return fuerzax,flag
            
def removalTH2(nodeI,nodeJ,ele,der):
    fuerza1 = [0]*6
    fuerza2 = [0]*6
    flag = 0
    d1= nodeDisp(nodeI,1)
    d2= nodeDisp(nodeJ,1)
    y1= nodeCoord(nodeI)[1]
    y2= nodeCoord(nodeJ)[1]
    deriva= (d2-d1)/(y2-y1)
    if abs(deriva) > der:
        remove('ele',ele[0])
        remove('ele',ele[1])
        flag = 1
    else:
        fuerza1 = eleForce(ele[0])
        fuerza2 = eleForce(ele[1])

    return fuerza1, fuerza2, flag