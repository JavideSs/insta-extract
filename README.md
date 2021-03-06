# Insta Extract
insta-extract is a command line application that scrapes instagram information.

---

## How to use it
### Running from source code
Python must be installed.

```
# Clone project
git clone https://github.com/JavideSs/insta-extract.git
cd insta-extract

# Run insta-extract
python main.py -h
```

## Usage examples

- **User info:**

``python main.py -l <user> <passw> -u <user_to_scraping>``

*If any other option has been used and you want to display the user information as well use the -i option:*  
``python main.py -l <user> <passw> -u <user_to_scraping> -i``

*To download the profile picture use the -dp option:*  
``python main.py -l <user> <passw> -u <user_to_scraping> -dp``

- **Posts info:**

*Of all posts:*  
``python main.py -l <user> <passw> -u <user_to_scraping> -p``

*At index counting from the last post as 0:*  
``python main.py -l <user> <passw> -u <user_to_scraping> -p 1``

*To download the posts found use the -dp option:*  
``python main.py -l <user> <passw> -u <user_to_scraping> -p -dp``

- **Followings usernames:**

``python main.py -l <user> <passw> -u <user_to_scraping> -f1 <file1.txt>``

- **Followers usernames:**

``python main.py -l <user> <passw> -u <user_to_scraping> -f2 <file2.txt>``

- **Compare usernames:**

``python main.py -c <file1.txt> <file2.txt>``

### Additional
Multiple options can be specified at the same time.  
Example to know followings not followers and vice versa:  
``python main.py -l <user> <passw> -u <user_to_scraping> -f1 <file1.txt> -f2 <file2.txt> -c <file1.txt> <file2.txt>``

When you login with the -l option the session is saved in the usersession file, it will be used for the following extractions. So it is not necessary to use the option while the file exists.

### Limitations
The instagram api limits unlogged users to only access a finite number of times and not extracting information from privates accounts, also:
- The option of followings and followers will not be available.
- Post information will have a limit of a range of the last 12 posts.

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
Javier Mellado S??nchez  
2021