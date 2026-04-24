from readcomics import ReadComicsOnline as Read

if __name__ == "__main__":
    input_link = input("Enter the comic issue link:\n>>")
    Read.get_issue_links(input_link)