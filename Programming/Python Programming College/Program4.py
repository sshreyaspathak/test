# numbers = [1, 2, 3]
# fruits = ["apple", "banana"]
# mixed = [1, "apple", True, 3.14]
#
# print("Numbers List:", numbers)
# print("Fruits List:", fruits)
# print("Mixed List:", mixed)
available_items = ["Apple", "Banana", "Mango", "Orange", "Pineapple", "Grapes"]
user_list = []

print("Available Items:")
for i, item in enumerate(available_items, start=1):
    print(f"{i}. {item}")

print("\nCreate your own list! (Type 'done' when finished)")

while True:
    choice = input("Enter the item number to add: ").strip()

    if choice.lower() == "done":
        break

    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(available_items):
            selected_item = available_items[choice - 1]
            if selected_item not in user_list:
                user_list.append(selected_item)
                print(f"✅ '{selected_item}' added to your list.")
            else:
                print("⚠ Item already in your list.")
        else:
            print("❌ Invalid number. Please select from the list.")
    else:
        print("❌ Please enter a valid number or 'done'.")

print("\nYour final custom list:", user_list)
