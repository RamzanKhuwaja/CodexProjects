import Common.my_utils as utils

def main():

    utils.set_campus_info("VAU")

    print("Entering Check to FindDupStudentsIn VAU BSViaClassList.")
    
    if utils.FindDupStudentsInBSViaClassList (utils.VAU_CLASS_LIST_DIR):
        print("Exiting Check on FindDupStudentsIn VAU BSViaClassList.")
        return True
    else:
        print("WARNING: Exiting Check on FindDupStudentsIn VAU BSViaClassList.")
        return False


if __name__ == "__main__":
    main()