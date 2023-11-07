"""
This program is written to familiarize with click's .group() and .option() tools
"""

import click
import math

# click group allows for multiple functions to be called via same script
@click.group()
def food():
    pass

@food.command()
@click.argument('name_of_order')
@click.option('--impossible', '-i', is_flag=True, help = 'Substitute beef patty for impossible patty.')
@click.option('--cheese', '-c', is_flag=True, help = 'Add cheese to burger.')
@click.option('--ketchup', '-k', is_flag=True, help = 'Add ketchup to burger.')
@click.option('--lettuce', '-l', is_flag=True, help = 'Add lettuce to burger.')
@click.option('--tomato', '-t', is_flag=True, help = 'Add tomato to burger.')
@click.option('--pickle', '-p', is_flag=True, help = 'Add pickles to burger.')
@click.option('--mushroom', '-m', is_flag=True, help = 'Add mushrooms to burger.')
def burger(name_of_order, impossible, cheese, ketchup, lettuce, tomato, pickle, mushroom):
    
    selected_options =[]
    total = 5.00
    order = f"Your order is named {name_of_order}."

    if impossible:
        click.echo('You have substituted for impossible meat.')
        selected_options.append('impossible meat')
        total += 1.00
    if cheese:
        click.echo('You have added cheese.')
        selected_options.append('cheese')
        total += 0.50
    if ketchup:
        click.echo('You have added ketchup.')
        selected_options.append('ketchup')
    if lettuce:
        click.echo('You have added lettuce.')
        selected_options.append('lettuce')
        total += 0.50
    if tomato:
        click.echo('You have added tomato.')
        selected_options.append('tomato')
        total += 0.50
    if pickle:
        click.echo('You have added pickles.')
        selected_options.append('pickles')
        total += 0.25
    if mushroom:
        click.echo('You have added mushrooms.')
        selected_options.append('pickles')
        total += 0.25
    
    options_text = ', '.join(selected_options)
    if options_text:
        click.echo(f"{order} Your burger includes {options_text}. The total is ${total:.2f}")
    else:
        click.echo(f"{order} No added ingredients/toppings. The total is ${total:.2f}")

@food.command()
@click.argument('name_of_order')
@click.option('--cheese', '-c', is_flag=True, help = 'Add cheese sauce to hotdog.')
@click.option('--mustard', '-m', is_flag=True, help = 'Add mustard to hotdog.')
@click.option('--ketchup', '-k', is_flag=True, help = 'Add ketchup to hotdog.')
@click.option('--relish', '-r', is_flag=True, help = 'Add relish to hotdog.')
def hotdog(name_of_order, cheese, mustard, ketchup, relish):
    
    selected_options =[]
    total = 2.50
    order = f"Your order is named {name_of_order}."

    if cheese:
        click.echo('You have added cheese sauce.')
        selected_options.append('cheese sauce')
        total += 0.15
    if mustard:
        click.echo('You have added mustard.')
        selected_options.append('mustard')
        total += 0.15
    if ketchup:
        click.echo('You have added ketchup.')
        selected_options.append('ketchup')
        total += 0.15
    if relish:
        click.echo('You have added relish.')
        selected_options.append('relish')    
        total += 0.15
    options_text = ', '.join(selected_options)
    if options_text:
        click.echo(f"{order} Your hot dog includes {options_text}. The total is ${total:.2f}")
    else:
        click.echo(f"{order} No added ingredients/toppings. The total is ${total:.2f}")

"""
# first function, hello
@click.command()
@click.argument('name')
@click.option('--uppercase', '-u', is_flag=True, help = 'Print name in uppercase.')
def hello(name, uppercase):
    #click.echo(f"Hello, {name}!")
    greeting = f"Hello, {name}!"
    if uppercase:
        greeting = greeting.upper()
    click.echo(greeting)
"""

if __name__ == '__main__':
    food()