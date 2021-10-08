import json

from Constants import ScriptLevel, IdentifierKey_Category, IdentifierKey_QandA

from Category import Category
from QandA import QandA


def TraverseScript(script : Category, level : int) -> Category:
    if level > 0:
        # No more actions to traverse, traverse failed
        if len(script.ActionList) <= 0:
            return None
        elif type(script.ActionList[len(script.ActionList) - 1]) is Category:
            return TraverseScript(script.ActionList[len(script.ActionList) - 1], level - 1)
        else:
            return None
    else:
        return script


def LoadScript(path : str, script : Category):
    # Open script file
    f = open(path, "r")
    # json.dump({"var1":"val1", "var2":"val2"}, f, indent=-1)
    
    buffer = ""
    level = 0
    for line in f:
        # Strip line of trailing white spaces, \n, and \t
        line = line.strip().rstrip("\n").lstrip("\t")

        # Condition checking to identify what line does
        if line.startswith(ScriptLevel):
            # Count number of level
            for s in line:
                if s == ScriptLevel:
                    level += 1
                else:
                    # Stop the moment it encounters something else
                    break
        # Look for opening curly braces
        elif buffer == "" and line.startswith("{"):
            buffer += line
        # Write content into buffer
        elif buffer != "":
            buffer += line

            # Find ending curly braces
            if line.startswith("}"):
                # Process buffer into Action
                dict = json.loads(buffer)

                # Check Script Traversable
                currentCategory = TraverseScript(script, level - 1)
                if currentCategory != None:
                    # Determine dict value belongs to which type
                    if IdentifierKey_Category in dict:
                        # Dict is a Category
                        currentCategory.AddAction(Category(
                            dict["Name"], 
                            dict["Message"]))
                    elif IdentifierKey_QandA in dict:
                        # Dict is a Q&A
                        currentCategory.AddAction(QandA(
                            dict["Question"], 
                            dict["Answer"], 
                            dict["Media"] if "Media" in dict else None))

                # Clear buffer after processing
                buffer = ""
                level = 0

    # Close script file
    f.close()

#LoadScript(DataDirectory + "Test.json", Category("Main", "Main Message"))