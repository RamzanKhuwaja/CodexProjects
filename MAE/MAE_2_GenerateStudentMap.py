import Common.my_utils as utils

def main():
    utils.set_campus_info("MAE")

    print("Entering MAE GenerateStudentMap")
        
    if utils.GenerateStudentMap("MAE"):
        print("Exiting MAE GenerateStudentMap")
        return True
    else:
        print("ERROR: Exiting MAE GenerateStudentMap")
        return False

if __name__ == "__main__":
    main()
