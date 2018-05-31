import numpy as np


class AlignNW:
    def __init__(self, equal_score=1, unequal_score=-1, space_score=-1):
        self.equalScore = equal_score
        self.unequalScore = unequal_score
        self.spaceScore = space_score

    def traceBack(self, list1, list2, scoreMatrix):
        '''
        Return:
             alignedList1, alignedList2, commonSub
        '''
        commonSub = []
        alignedList1 = []
        alignedList2 = []
        alignedList = []
        i, j = scoreMatrix.shape[0] - 1, scoreMatrix.shape[1] - 1
        if i == 0 or j == 0:
            return list1, list2, alignedList
        else:
            while i != 0 and j != 0:  # 顺序是左上，上，左
                if list1[i - 1] == list2[j - 1]:
                    commonSub.append(list1[i - 1])
                    alignedList.append(list1[i-1])
                    alignedList1.append(list1[i - 1])
                    alignedList2.append(list2[j - 1])
                    i -= 1
                    j -= 1
                elif scoreMatrix[i][j] == scoreMatrix[i - 1][j - 1] + self.unequalScore:
                    alignedList.append('*')
                    alignedList1.append(list1[i - 1])
                    alignedList2.append(list2[j - 1])
                    i -= 1
                    j -= 1
                elif scoreMatrix[i][j] == scoreMatrix[i - 1][j] + self.spaceScore:
                    alignedList.append('*')
                    alignedList1.append(list1[i - 1])
                    alignedList2.append('_')
                    i -= 1
                else:  # scoreMatrix[i][j] == scoreMatrix[i][j-1] + self.spaceScore:
                    alignedList.append('*')
                    alignedList1.append('_')
                    alignedList2.append(list2[j - 1])
                    j -= 1
        # 己回溯到最左一行，或最上一列，但未到达0, 0 位置
        while i > 0:
            alignedList1.append(list1[i - 1])
            alignedList.append('*')
            i -= 1
        while j > 0:
            alignedList2.append(list2[j - 1])
            alignedList.append('*')
            j -= 1
        alignedList1.reverse()
        alignedList2.reverse()
        commonSub.reverse()
        alignedList.reverse()
        #print("test: commonSub:{}".format(commonSub))
        return alignedList1, alignedList2, alignedList

    def createScoreMatrix(self, list1, list2, debug=False):
        lenList1, lenList2 = len(list1), len(list2)
        # initialize matrix
        scoreMatrix = np.zeros((lenList1 + 1, lenList2 + 1), dtype=int)
        for i in range(1, lenList1 + 1):
            scoreMatrix[i][0] = i * self.spaceScore
        for j in range(1, lenList2 + 1):
            scoreMatrix[0][j] = j * self.spaceScore
        # populate the matrix
        for i, x in enumerate(list1):
            for j, y in enumerate(list2):
                if x == y:
                    scoreMatrix[i + 1][j + 1] = scoreMatrix[i][j] + self.equalScore
                else:
                    scoreMatrix[i + 1][j + 1] = max(scoreMatrix[i][j + 1] + self.spaceScore,
                                                    scoreMatrix[i + 1][j] + self.spaceScore,
                                                    scoreMatrix[i][j] + self.unequalScore)
        if debug:
            print("score Matrix:")
            print(scoreMatrix)
        return scoreMatrix

    #Needleman-wunsch only have one result.
    def doAlign(self, list1, list2, debug=False):
        scoreMatrix = self.createScoreMatrix(list1, list2, debug)
        return self.traceBack(list1, list2, scoreMatrix)


## for test
#if __name__ == "__main__":
#    aligner = AlignNW(1, -1, -2)
#    #list1 = list("GCCCTAGCG")
#    #list2 = list("GCGCAATG")
#    list1 = list("GCCTAGCG")
#    list2 = list("CGCAATG")
#    alignedList1, alignedList2, alignedTextList = aligner.doAlign(list1, list2)
#    print("alignedList1: {} \nalignedList2: {} \nalignedTextList: {}."
#          .format(alignedList1, alignedList2, alignedTextList))
