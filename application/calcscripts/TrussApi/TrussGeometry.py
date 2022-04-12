from PrattTrussGeometry.Geometry import Geometry


class TrussGeometry(object):
    """
    Class to generate truss geometry from simple inputs
    """

    def __init__(self, span, height, nVertWebsPerSide=1, trussType='PrattRoofTruss'):
        self.type = trussType
        self.truss = Geometry(span, height, nVertWebsPerSide)

    def getNodesDict(self):
        nodes = self.truss.getNodes()
        nd = {}
        for i in range(len(nodes)):
            node = nodes[i]
            nd[i] = {'x': node.x, 'y': node.y, 'fixity': node.fixity}
        return nd

    def getMembersDict(self):
        members = self.truss.getMembers()
        md = {}
        for i in range(len(members)):
            mem = members[i]
            md[i] = {'start': mem.start, 'end': mem.end, 'type': mem.member_type}
        return md

    def getTruss(self):
        return self.truss
