import inquirer


def ask_run_code_confirm(message='Would you like to run this code? (y/n)\n\n'):
    questions = [inquirer.Confirm('confirm', message=message)]
    answers = inquirer.prompt(questions)
    return answers["confirm"]
