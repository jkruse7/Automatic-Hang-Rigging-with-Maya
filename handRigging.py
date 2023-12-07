import maya.cmds as cmds


def rigFinger(joint, count):

    children = cmds.listRelatives(joint, ad=True) # get the other joints in finger
    num_circles = len(children)
    curr = joint
    i=num_circles
    counter = 1

    #GENERATE THE NURBS CIRCLES
    while i>0:
        circle_name = "circle_" + str(count) + "_"+ str(counter) 
        cmds.circle(c=[0, 0, 0], nr=[1, 0, 0], sw=360, r=1, d=3, ut=False, tol=0.01, s=8, ch=True, name=circle_name)
        cmds.select(circle_name, r=True)
        parent_name = "offset_index_" + str(count) + "_" + str(counter)
        if(counter>1):
            cmds.group(circle_name,p="circle_"+ str(count) + "_"+str(counter-1),name=parent_name) #group under parent
        else:
            cmds.group(circle_name,name=parent_name)
        counter += 1
        i-=1
        curr = children[i]
    #MOVE TO THE JOINTS  
    i = num_circles
    curr = joint
    num = 1

    while i>0:
        if(num == 1):
            worldPos = cmds.xform(curr, q=True, ws=True, t=True) # find where to place around joints
        else:
            worldPos = cmds.getAttr(curr +'.translate')
            worldPos = list(worldPos[0])
        cmds.xform("offset_index_"+ str(count) + "_"+str(num), t =worldPos) #move translate
        i-=1
        num += 1
        curr=children[i]
    #CONTRAIN PARENT
    #This is to ensure that their x vectors are going in the same direction
    num=1
    i = num_circles
    curr = joint
    while(i>0):
        result = cmds.parentConstraint(curr, "offset_index_"+ str(count) + "_"+str(num), mo=False)
        cmds.delete(result) #delete the constraint after
        i-=1
        num += 1
        curr=children[i]

    #PUT TRANSLATIONS INTO OFFSET APRENT MATRIX
    num=1
    i = num_circles
    curr = joint
    while(num<=num_circles):
        var = "offset_index_"+ str(count) + "_"+str(num)
        cmds.connectAttr( var + ".matrix", var + ".offsetParentMatrix", f=True)
        cmds.disconnectAttr(var + ".matrix", var + ".offsetParentMatrix") #disconnect so we can change the original transform
        cmds.xform(var, t =[0,0,0], ro = [0,0,0]) #set original transform to zeros
        num += 1
    #CONTRAIN TO JOINTS (again)
    num=1
    i = num_circles
    curr = joint
    while(i>0):
        result = cmds.parentConstraint("circle_"+ str(count) + "_"+str(num), curr, mo=True)
        i-=1
        num += 1
        curr=children[i]
    

selectionList = cmds.ls(orderedSelection=True) #wrist should be selected
count = 1
for obj in selectionList:
    joints = cmds.listRelatives(obj, ad=False) #find the main finger joints
    joints = joints[0:5] #only do the five fingers (in case any constraints here)  
    worldPos = cmds.xform(obj, q=True, ws=True, t=True)
    total_ctl = cmds.circle(c=worldPos,nr=(0,1,0),name = "CTL_Fingers") #this is the big control
    cmds.xform('CTL_Fingers', t =(8,0,0))
    cmds.move(worldPos[0], worldPos[1], worldPos[2], 'CTL_Fingers.scalePivot', 'CTL_Fingers.rotatePivot', absolute=True)#move pivot to be on the wrist joint
    for joint in joints: #go through the fingers
        rigFinger(joint, count)
        cmds.parent("offset_index_" +str( count) + "_1", "CTL_Fingers") #set underneath the big control
        count += 1
    # constrain finger control to the wrist
    cmds.pointConstraint(obj, "CTL_Fingers", mo = True)
    cmds.orientConstraint(obj, "CTL_Fingers", mo = True)
    #set up finger curl and finger spread
    #make attributes in channel box
    cmds.addAttr("CTL_Fingers", k= True,dv =0.0, ln = "FingersCurl", max= 5.0, min = -70.0)
    cmds.addAttr("CTL_Fingers", k= True,dv =0.0, ln = "FingersSpread", max = 30.0, min = -5.0)
    #set finger curl
    offsets = cmds.listRelatives("CTL_Fingers", ad=True)
    for ctl in offsets:
        if ctl.startswith("offset"):
            cmds.connectAttr("CTL_Fingers.FingersCurl", ctl + ".rz", f=True)
    #set finger spread
    offsets = cmds.listRelatives("CTL_Fingers", ad=False)
    for ctl in offsets:
        #each spread is slightly different
        if ctl.startswith("offset_index_1"):
            #index finger
            node =  cmds.shadingNode("multDoubleLinear", au=True)
            cmds.connectAttr("CTL_Fingers.FingersSpread",node + ".input1", f=True)
            cmds.setAttr(node + ".input2", -1.0) #multiply so it moves in opposite direction
            cmds.connectAttr(node+".output", ctl+".ry", f=True)
        if ctl.startswith("offset_index_2"):
            #pinky finger
            node =  cmds.shadingNode("multDoubleLinear", au=True)
            cmds.connectAttr("CTL_Fingers.FingersSpread",node + ".input1", f=True)
            cmds.setAttr(node + ".input2", 1.0)
            cmds.connectAttr(node+".output", ctl+".ry", f=True)
        if ctl.startswith("offset_index_3"):
            #ring finger
            node =  cmds.shadingNode("multDoubleLinear", au=True)
            cmds.connectAttr("CTL_Fingers.FingersSpread",node + ".input1", f=True)
            cmds.setAttr(node + ".input2", 0.5) #this only moves half as much in that direction
            cmds.connectAttr(node+".output", ctl+".ry", f=True)
        if ctl.startswith("offset_index_4"):
            #middle finger
            node =  cmds.shadingNode("multDoubleLinear", au=True)
            cmds.connectAttr("CTL_Fingers.FingersSpread",node + ".input1", f=True)
            cmds.setAttr(node + ".input2", -0.5) # this moves half as much in opposite direction
            cmds.connectAttr(node+".output", ctl+".ry", f=True)
            
    #MAKE THE OVERALL FINGER CURVE
    


