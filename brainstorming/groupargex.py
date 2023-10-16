import click

# Define a decorator factory that accepts arguments
def user_group_decorator(user_type, is_admin):
    def decorator(f):
        def wrapper(*args, **kwargs):
            click.echo(f"User Type: {user_type}, Is Admin: {is_admin}")
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Create a Click group and apply the decorator
@click.group()
@user_group_decorator(user_type='regular', is_admin=False)
def user():
    pass

# Define a command within the group
@user.command()
def list_users():
    click.echo("Listing users")

# Define another command within the group
@user.command()
def add_user():
    click.echo("Adding a user")

if __name__ == '__main__':
    user()
