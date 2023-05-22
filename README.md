# Themis submitter

Command-line tool to test your solutions in the best on-line problem judge - themis

## How to install

```bash
pip install .
```

## How to configure

Pase your login and password into 'themis-submitter.py' file, lines 13 and 14 (super secure)

## How to use

You can list all attending groups with the command:

```bash
list groups
```

and list all tasks from the group you attend:

```bash
list tasks <group_name>
```

And finally, you can submit your solution with a command:

```bash
submit <group_name> <task_name> <path to file>
```

The script will automatically detect your language based on file extension.

## License

[MIT](./LICENSE)
