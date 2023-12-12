# Ideas for Implementation:

## Helpful Click Decorators & Utilities
* click's `--help` option will be ideal for users
* `click.option()`: this will be very useful for flags that may be used
    - will be able to use commands like `is_flag`, `flag_value`, `count`, `help`, etc.
* `click.group()`: this will allow FRE to be broken up into parts and subparts for each part
    - will be able to use commands like `add_command`
* `click.progressbar()`: potential for the user to see progress while something runs like `fre run`
* `click.confirm()`: potential for the user to verify actions and proceed
* `click.style()`: can style text with wanted configurations if needed (can use click.secho())
* `click.pause()`: stops executing current command and waits for user input to continue
* `click.pass_context`: allows use of `context.forward(command)` and `context.invoke(command, args)` for discouraged yet possible invocation of commands from another command, probably what is going to be the solution to running all of something like `fre make` at once

## Potential Errors
* `click.confirm()` actions will be hard for users to script

## Questions for Users/Devs
* do we want to use flags (`click.option()`), confirmations (`click.confirm()`), or a mix of both to allow users to run what they want, how they want?
    - this means that users can either use certain flags (i.e `--execute`), which will be included and explained in the `--help` feature, or they will just be prompted for what features they want and can decide if they want it with [y/N]

## Things to Consider/Implement
* use of classes, arguments (necessary) vs. flags (optional)
    - arguments can be used for specific cases; i.e need to parse specific file
* NOAA GFDL Conda channel to get this into userspace (Conda > pip/venv)

## Required Changes to Make
* `fre pp configure -y file.yaml` only works when inside folder containing schema at the moment
* want to polish up .gitignore file
* deployment via GitLab
* is there a way to check that all python dependencies needed by fre-cli are available in the current python envioronment? Like "python fre.py" or something?

## Potential Additional Uses for Click
* program using BeautifulSoup to scrape GFDL pages for immediate tutorial guidance after prompting for GFDL login