import smtplib, ssl
import sys

problems_filepath = '../data/problems.csv'
problems_mapping = {}

def read_problems():
    with open(problems_filepath) as f:
        line = f.readline()
        while line:
            if line.strip() != '':
                problem = line.strip().split(' -> ')
                problems_mapping[problem[0]] = problem[1]
                line = f.readline()
            else:
                break

def send_email(receiver_email,assignment,person):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "murrayfamilystockings@gmail.com"  # Enter your address
    password = "Miles99!"
    subject = person + " -- The Murray Family Stocking Exchange"
    body = "You are filling the stocking of " + assignment
    message = """\
    Subject: """ + subject + """

     """ + body + ""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def num_mapping(size):
    from random import shuffle
    mapping = {}
    listing = [i for i in range(size)]
    shuffle(listing)
    last = listing[-1]
    for i in range(len(listing)-1):
        first = listing[i]
        second = listing[i+1]
        mapping[first] = second
    mapping[last] = listing[0]
    return mapping

def create_assignment(people):
    num_map = num_mapping(len(people))
    people_list = [i for i in people]
    people_map = {}
    for entry in num_map:
        people_map[people_list[entry]] = people_list[num_map[entry]]
    if not check_problems(people_map):
        create_assignment(people)
    return people_map

def check_problems(people_map):
    for person1 in people_map:
        if person1 in problems_mapping:
            if people_map[person1].lower() == problems_mapping[person1].lower():
                return False
    return True

def add_new_problem(person1,person2):
    f = open(problems_filepath, "a")
    f.write("%s -> %s\n" % (person1, person2))
    f.close()

def user_input_check_problems(assignment,people):
    user_not_done = True
    while user_not_done:
        problems = input('If there are any problems with this matching, '
                         'press \'y\'. Otherwise, just press enter.\n')
        if problems == 'y':
            still_problems = True
            while still_problems:
                person1 = input('Enter the person who is not allowed to do the buying '
                                '(for example if Lisa cannot buy for Sue, this would be Lisa)\n')
                person2 = input('Enter the person who is not allowed to do the receiving '
                                '(for example if Lisa cannot buy for Sue, this would be Sue)\n')
                add_new_problem(person1, person2)
                read_problems()
                keep_going = input('New rule added. Are there any more problems? '
                                   'If yes press \'y\', if not press enter.\n')
                if keep_going != 'y':
                    still_problems = False
            assignment = create_assignment(people)
            print('The new assignment is as follows:')
            display_assignment(assignment)
        else:
            user_not_done = False
    return assignment

def display_assignment(assignment):
    for map in assignment:
        print(map + ' -> ' + assignment[map])

def main():
    people = {}
    read_problems()
    print('Welcome to the Murray Family Stocking Exchange, made easy.')

    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        with open(filepath) as f:
            line = f.readline()
            while line:
                split = line.strip().split(', ')
                name = split[0]
                email = split[1]
                people[name] = email
                line = f.readline()
        print('Successfully read data from file.')

    elif len(sys.argv) == 1:
        print('First, you need to input all of the peoples\' names and emails. Do this in the form:  '
              'John Doe, example@email.com (the comma is necessary)\n'
              'When done, press enter')
        entry = ' '
        while entry != '':
            entry = input('> ')
            if entry != '':
                split = entry.split(', ')
                if len(split) != 0:
                    name = split[0]
                    email = split[1]
                    people[name] = email
                else:
                    print('Invalid format. Try again')
        print('Completed adding people. \n'
              'If the following looks correct, press enter. If not...terminate the program and try again.')
        for person in people:
            print('Name: ' + person + ' Email: ' + people[person])
    else:
        print('Error in program arguments')

    assignment = create_assignment(people)
    print('\nCreated assignment.\nWould you like to see the assignment of who is buying for who? '
          'Type \'y\' for yes and \'n\' for no, then press enter.\n')
    nopref = True
    while nopref:
        preference = input('> ')
        if preference == 'y':
            nopref = False
            display_assignment(assignment)
            assignment = user_input_check_problems(assignment, people)
        elif preference == 'n':
            nopref = False
        else:
            print('That is not a valid input. Try again.')

    input('When you are ready to send the emails with assignments, press enter.')

    for person in people:
        print("Sending to "+person+" to buy for "+assignment[person])
        try:
            send_email(people[person],assignment[person],person)
            print('Sent assignment to '+people[person])
        except:
            print('An error occurred when trying to send the email. '
                  'Check to make sure you are connected to the internet.')

main()