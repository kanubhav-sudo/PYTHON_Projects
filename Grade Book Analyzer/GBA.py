print("Grade Book Analyzer !!!!")


num_students = int(input("Enter number of students: "))
names = [None] * num_students
marks = [0] * num_students

for i in range(num_students):
    name = input("Enter name of student " + str(i+1) + ": ")
    mark = int(input("Enter marks of " + name + ": "))
    names[i] = name
    marks[i] = mark

total = 0
for m in marks:
    total = total + m

average = total / num_students
highest = max(marks)
lowest = min(marks)

print("\n--- Student Report ---")
for i in range(num_students):
    if marks[i] >= 90:
        grade = "A"
    elif marks[i] >= 80:
        grade = "B"
    elif marks[i] >= 70:
        grade = "C"
    elif marks[i] >= 60:
        grade = "D"
    elif marks[i] >= 50:
        grade = "E"    
    else:
        grade = "F"
    
    print("Name:", names[i], "| Marks:", marks[i], "| Grade:", grade)


print("\n--- Overall Analysis ---")
print("Total Marks of Class:", total)
print("Average Marks of Class:", average)
print("Highest Marks:", highest, "by", names[marks.index(highest)])
print("Lowest Marks:", lowest, "by", names[marks.index(lowest)])
