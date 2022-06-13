import numpy as np
from StructPy.Truss import Truss
from TrussAnalysis.TrussUtilities.MemberType import MemberType
from StructPy.cross_sections import generalSection
from StructPy.materials import Custom
from TrussAnalysis.TrussUtilities.Forces import Forces
from application.calcscripts.TrussApi.TrussGeometry import TrussGeometry


class TrussAnalysis(TrussGeometry):
    """
    Class to generate truss geometry and analysis from simple inputs
    """

    def __init__(self, span, height, nVertWebsPerSide=1, trussType='PrattRoofTruss', eMod=None, aCross=None):
        super().__init__(span, height, nVertWebsPerSide, trussType)
        if aCross is None:
            aCross = {"top": 1, "bot": 1, "web": 1}
        if eMod is None:
            eMod = {"top": 1000, "bot": 1000, "web": 1000}
        self.xsMemberType = {MemberType.topChord: generalSection(1, 1, aCross.get("top")),
                             MemberType.botChord: generalSection(1, 1, aCross.get("bot")),
                             MemberType.diaWeb: generalSection(1, 1, aCross.get("web")),
                             MemberType.vertWeb: generalSection(1, 1, aCross.get("web"))}
        self.materialMemberType = {MemberType.topChord: Custom(eMod.get("top"), 1),
                                   MemberType.botChord: Custom(eMod.get("bot"), 1),
                                   MemberType.diaWeb: Custom(eMod.get("web"), 1),
                                   MemberType.vertWeb: Custom(eMod.get("web"), 1)}
        self.xsDefault = generalSection(1, 1, 1)
        self.materialDefault = Custom(1000, 10)
        self.forces = Forces(self.truss.getNNodes())
        self.analysisTruss = Truss(cross=self.xsDefault, material=self.materialDefault)
        self.__initAnalysisTruss()

    def __initAnalysisTruss(self):
        for node in self.truss.getNodes():
            self.analysisTruss.addNode(node.x, node.y, fixity=node.fixity)
        for mem in self.truss.getMembers():
            xs = self.xsMemberType.get(mem.member_type)
            mat = self.materialMemberType.get(mem.member_type)
            self.analysisTruss.addMember(mem.start, mem.end, cross=xs, material=mat)

    def setNodeForces(self, forceArray=None):
        if forceArray is None:
            forceArray = [[0, 0, 0]]
        for force in forceArray:
            self.forces.setForceAtNode(force[0], force[1], force[2])

    def getStructureResults(self):
        displacements = self.analysisTruss.directStiffness(np.array(self.forces.forces)).tolist()
        memberForces = []
        for i in range(len(self.analysisTruss.members)):
            member = self.analysisTruss.members[i]
            memberForces.append([i, member.SN.n, member.EN.n, member.length, member.axial])
        return memberForces, ['Member ID', 'Start Node', 'End Node', 'Length', 'Axial Force'], displacements

    def getMemberStiffness(self, memIndex):
        return self.analysisTruss.members[memIndex].kglobal.tolist()

    def getGlobalStiffnessMatrix(self):
        return self.analysisTruss.K.tolist()

    def getReducedGlobalStiffnessMatrix(self):
        return self.analysisTruss.reducedK.tolist()

    def getReducedForceMatrix(self):
        return np.array(self.forces.forces)[self.analysisTruss.freeDoF].tolist()
