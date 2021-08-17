# Insta Extract
insta-extract is a command line application that scrapes instagram information.

![Screenshot](images/user_info.jpg?raw=true "App interface")

---

## How to use it
### Running from source code
Python must be installed.

```
# Clone project
git clone https://github.com/JavideSs/insta-extract.git
cd insta-extract

# Run reproc
python main.py -h
```

## Usage examples

**User info:**  
``python main.py -l <user> <passw> -u <user_to_scraping>``

**Posts info (at index counting from the last post as 0):**  
``python main.py -l <user> <passw> -u <user_to_scraping> -p``  
``python main.py -l <user> <passw> -u <user_to_scraping> -p 1``

**Followings usernames:**  
``python main.py -l <user> <passw> -u <user_to_scraping> -f1 <file1.txt>``

**Followers usernames:**  
``python main.py -l <user> <passw> -u <user_to_scraping> -f2 <file2.txt>``

**Compare usernames:**  
``python main.py -c <file1.txt> <file2.txt>``

### Additional
Multiple options can be specified at the same time.  
Example to know followings not followers and vice versa:  
``python main.py -l <user> <passw> -u <user_to_scraping> -f1 <file1.txt> -f2 <file2.txt> -c <file1.txt> <file2.txt>``


### Limitations
The instagram api limits unlogged users to only access a finite number of times and not extracting information from privates accounts, also the option of followings and followers will not be available.

Post information has a limit of a range of the last 12 posts.

Username comparisons should be as the output format of the followings and followers options.

---

## Dependencies
It has not been extensively tested yet. The following dependencies have been tested while developing on Windows 10.
- Python 3.7.4.

---

## Feedback
Your feedback is most welcomed by filling a
[new issue](https://github.com/JavideSs/insta-extract/issues/new).

---

Author:  
Javier Mellado Sánchez  
2021