import Common.my_utils as utils

def main():

    utils.set_campus_info("MAE")

    print("Entering Check to FindDupStudentsIn MAE BSViaClassList.")
    
    if utils.FindDupStudentsInBSViaClassList (utils.MAE_CLASS_LIST_DIR):
        print("Exiting Check on FindDupStudentsIn MAE BSViaClassList.")
    else:
        print("WARNING: Exiting Check on FindDupStudentsIn MAE BSViaClassList.")


if __name__ == "__main__":
    main()   