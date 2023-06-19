"""generates a maze.
Inputs:
centers: the centers of the cells
u: the number of rows
v: the nomber of columns
Output:
maze: the created maze"""


from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class maze(component):


    def RunScript(self, cellCenters, u, v, cellLines):

        __author__ = "k4rm3n"
        __version__ = "2021.10.16"
                
        import rhinoscriptsyntax as rs
        import ghpythonlib.treehelpers as gt 
        import Rhino as rh
        from Grasshopper import DataTree as dp
        import Grasshopper as gh
        import random

        maze = None

        def nest_list(list,columns, rows):
            nestList=[]               
            start = 0
            end = columns
            for i in range(rows): 
                nestList.append(list[start:end])
                start += columns
                end += columns
            return nestList
                
        def listToTree(nestedList):
            dt = gh.DataTree[object]()
            for i,j in enumerate(nestedList):
                dt.AddRange(j,gh.Kernel.Data.GH_Path(i))
            return dt
        
        a = nest_list(cellCenters,v,u)
        tr = listToTree(a)

        def tree_route(tree,element, columns, rows):
            for i in range(0,rows):
                pth = gh.Kernel.Data.GH_Path(i)
                branchTree = tree.Branch(pth)
                for j in range(0,columns):
                    if branchTree[j]==element:
                        return i,j

        def horizontal_neighbours(tree,visCell, columns, rows):
            for i in range(0,rows):
                pth = gh.Kernel.Data.GH_Path(i)
                branchTree = tree.Branch(pth)
                for j in range(0,columns):
                    if branchTree[j]==visCell:
                        horiz_nhgbrs = []
                        if j==0:
                            horiz_nhgbrs.append(tree.Branch(pth)[j+1])
                        elif j == columns - 1:
                            horiz_nhgbrs.append(tree.Branch(pth)[j-1])
                        else:
                            horiz_nhgbrs.append(tree.Branch(pth)[j+1])
                            horiz_nhgbrs.append(tree.Branch(pth)[j-1])
                        return horiz_nhgbrs

        def vertical_neighbours(tree,visCell, rows, columns):
                for i in range(0,rows):
                    pth = gh.Kernel.Data.GH_Path(i)
                    branchTree = tree.Branch(pth)
                    for j in range(0,columns):
                        if branchTree[j]==visCell:
                            vertical_nhgbrs = []
                            if i == 0:
                                pu = gh.Kernel.Data.GH_Path(i+1)
                                vertical_nhgbrs.append(tree.Branch(pu)[j])
                            elif i == rows - 1:
                                pu = gh.Kernel.Data.GH_Path(i-1)
                                vertical_nhgbrs.append(tree.Branch(pu)[j])
                            else:
                                pu = gh.Kernel.Data.GH_Path(i+1)
                                vertical_nhgbrs.append(tree.Branch(pu)[j])
                                pe = gh.Kernel.Data.GH_Path(i-1)
                                vertical_nhgbrs.append(tree.Branch(pe)[j])
                            return vertical_nhgbrs
                
        def flattenTree(tree):
            flt = tree.Flatten()
            return flt
                
        def flattenNestedList(nestedList):
            newList = []
            for list in nestedList:
                for item in list:
                    newList.append(item)
                return newList

        def common_data(list1, list2):
            for x in list1:
                for y in list2:
                    if x == y:
                        result = True
                        return result 
                
                
        queue = list(cellCenters)
        visited = [False for i in range(0, len(queue))]
        stack = []
        pathlines = []
                
        idx = random.randrange(0,len(queue),1)
                
                
        visitedCell = cellCenters[idx]
        visited[idx] = True
                
        stack.append(visitedCell)
                
        while len(stack) > 0:
            neig = []
            ver = vertical_neighbours(tr, visitedCell, u, v)  
            hor = horizontal_neighbours(tr,visitedCell,v,u)
            neig = ver + hor
                
            check = []
            for i in neig:
                check.append(cellCenters.index(i)) 
            for i in check:
                if visited[i] == True:
                    neig.remove(cellCenters[i])
                
            if len(neig) != 0:
                next = random.choice(neig)
                prev = visitedCell
                idx = cellCenters.index(next)
                visited[idx] = True
                stack.append(next)
                ln = rs.AddLine(prev,next)
                pathlines.append(ln)
                visitedCell = queue[idx] 
                
            else: 
                visitedCell = stack.pop()

        def intersection(listLines1,listLines2):
            rslt = []
            iter = []
            intersct = []
            count = 0
            for ln1 in listLines1:
                for ln2 in listLines2:
                    rslt.append(rs.CurveCurveIntersection(ln1,ln2))
            for int in rslt:
                    if int != None:
                        iter.append(int)
            for itm in iter:
                        if itm not in intersct:
                             intersct.append(itm)
            return intersct

        pathXcell = intersection(pathlines,cellLines)

        intersections = gt.list_to_tree(pathXcell)

        ptIntersct = []
        for brn in range(0,intersections.BranchCount):
            branchList = intersections.Branch(brn)
            for jn in range(branchList.Count):
                ptIntersct.append(branchList[1])
                
        for elm in ptIntersct:
            for w in ptIntersct:
                if w == elm:
                    ix = ptIntersct.index(w)
                    ptIntersct.remove(w)


        for elm in ptIntersct:
            for w in ptIntersct:
                if w == elm:
                    ix = ptIntersct.index(w)
                    ptIntersct.remove(w)

        pattrn = [False for i in range(0, len(cellLines))]
        dist = []
        for i in range(0,len(cellLines)):
            for k in range(0, len(ptIntersct)):
                if 0.0 <= rs.LineMinDistanceTo(cellLines[i],ptIntersct[k]) < 0.1:
                    pattrn[i] = True
                
        maze = []
        for i,j in enumerate(pattrn):
            if j == False:
                maze.append(cellLines[i])
        return maze
