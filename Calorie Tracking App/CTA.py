print("Welcome to the Calorie Tracking App!")

calories = []   
total = 0    

while True:
    print("\nMenu:")
    print("1. Add a meal (enter calories)")
    print("2. View all meals")
    print("3. View total calories")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        name=input("Enter meal name: ")
        cal = int(input("Enter calories for the meal: "))
        calories.append(cal)
        total = total + cal
        print("Meal added successfully!")

    elif choice == "2":
        if len(calories) == 0:
            print("No meals recorded yet.")
        else:
            print("Your calorie entries:")
            for i in range(len(calories)):
                print("Meal", i+1, ":", calories[i], "calories")

    elif choice == "3":
        print("Total calories consumed today:", total)

    elif choice == "4":
        print("Exiting the app. Stay healthy!")
        break

    else:
        print("Invalid choice, please try again.")
