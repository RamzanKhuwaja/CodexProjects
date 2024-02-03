import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")
    print("Entering Check on MAE_CLASS_MAP_FILE.")
    if utils.check_class_map(utils.MAE_CLASS_MAP_FILE):
        print("Exiting Check on MAE_CLASS_MAP_FILE.")
        return True
    else:
        print("ERROR: Exiting Check on MAE_CLASS_MAP_FILE.")
        return False
    
    
if __name__ == "__main__":
    main()
