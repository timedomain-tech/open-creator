from prompt_toolkit.styles import Style


style = Style.from_dict(style_dict={
    # Default completion (not selected)
    'completion-menu.completion': 'bg:#ffffff #000000',  # White background with black text for unselected completions
    'completion-menu.completion.current': 'bg:#0000ff #ffffff',  # Blue background with white text for selected completion

    # Matched text
    'completion-menu.completion.current.match': 'fg:#00ffff',  # Light blue text for matched characters in selected completion
    'completion-menu.completion.match': 'fg:#0000ff',  # Blue text for matched characters in unselected completions

    # Non-matched text
    'completion-menu.completion.current.non-match': 'fg:#ffffff',  # White text for non-matched characters in selected completion
    'completion-menu.completion.non-match': 'fg:#000000',  # Black text for non-matched characters in unselected completions

    # Scrollbar
    'scrollbar.background': 'bg:#d0d0d0',  # Light gray background for scrollbar
    'scrollbar.button': 'bg:#222222',  # Dark color for scrollbar button

    'prompt': 'ansigreen',
    'stderr': 'red',
    "system": "ansiblue",
})
