import Common.my_utils as utils

def main():
    utils.set_campus_info("VAU")

    print("Entering VAU GenerateStudentMap")
        
    if utils.GenerateStudentMap("VAU"):
        print("Exiting VAU GenerateStudentMap")
        return True
    else:
        print("ERROR: Exiting VAU GenerateStudentMap")
        return False

if __name__ == "__main__":
    main()
