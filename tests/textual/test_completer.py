

if __name__ == "__main__":
    from completer import SuggestFromDict
    from constants import SUGGESTOR_TREE
    suggester = SuggestFromDict(SUGGESTOR_TREE)
    suggestions = suggester._get_suggestions_for_value("sa")
    print(suggestions)
    suggestions = suggester._get_suggestions_for_value(value=".")
    print(suggestions)
    suggestions = suggester._get_suggestions_for_value("save -")
    print(suggestions)
    suggestions = suggester._get_suggestions_for_value(value="create -")
    print(suggestions)
    suggestions = suggester._get_suggestions_for_value(value="adsfasd create -")
    print(suggestions)
    suggestions = suggester._get_suggestions_for_value(value="skill.")
    print(suggestions)

    suggestions = suggester._get_suggestions_for_value(value="skill .")
    print(suggestions)
