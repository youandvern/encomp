import numpy as np
from StructPy.Truss import Truss
from StructPy.cross_sections import HSS
from StructPy.materials import A992
from TrussAnalysis.TrussUtilities.Forces import Forces
from application.calcscripts.TrussApi.TrussGeometry import TrussGeometry


class TrussAnalysis(TrussGeometry):
    """
    Class to generate truss geometry and analysis from simple inputs
    """

    def __init__(self, span, height, nVertWebsPerSide=1, trussType='PrattRoofTruss'):
        super().__init__(span, height, nVertWebsPerSide, trussType)
        self.xsDefault = HSS(2, 1.75, 2, 1.75)
        self.materialDefault = A992()
        self.forces = Forces(self.truss.getNNodes())
        self.analysisTruss = Truss(cross=self.xsDefault, material=self.materialDefault)
        self.__initAnalysisTruss()

    def __initAnalysisTruss(self):
        for node in self.truss.getNodes():
            self.analysisTruss.addNode(node.x, node.y, fixity=node.fixity)
        for mem in self.truss.getMembers():
            self.analysisTruss.addMember(mem.start, mem.end)

    def setNodeForces(self, forceArray=None):
        if forceArray is None:
            forceArray = [[0, 0, 0]]
        for force in forceArray:
            self.forces.setForceAtNode(force[0], force[1], force[2])

    def getMemberForces(self):
        deformations = self.analysisTruss.directStiffness(np.array(self.forces.forces))
        memberForces = []
        for i in range(len(self.analysisTruss.members)):
            member = self.analysisTruss.members[i]
            memberForces.append([i, member.SN.n, member.EN.n, member.length, member.axial])
        return memberForces, ['Member ID', 'Start Node', 'End Node', 'Length', 'Axial Force']
