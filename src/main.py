from tree_search import find_bf, choice_search, TreeSearchMemoTree, TreeSearchNode
from graph_search import choice_search as gs_choice_search
from graph_search import find_bf as gs_find_bf
from common import simplify_bf
from words import tree_to_leafs, tree_to_words

import argparse
import time
import sys

def generate(input_token=None, output_file=None, graph_search=False, show_trees=False, show_leaves=False, show_time=False):
    # Read input from file or prompt the user
    if input_token:
        if len(input_token) == 1 and os.path.isfile(input_token):
            try:
                with open(input_token, "r") as f:
                    user_in = f.read()
            except FileNotFoundError:
                print(f"Error: The file '{input_token}' does not exist.")
                return
        else:
            user_in = input_token
    else:
        user_in = input("Enter bf program to process: ")
    bf = simplify_bf(user_in)
    if bf != user_in:
        print('Simplified brainfuck to functional equivalence\n')

    # process user input
    if graph_search:
        stime = time.time()
        paths = gs_find_bf(bf)
        if show_time:
            print(time.time()-stime)
        for p in paths:
            for n in p:
                if n.tree:
                    print('(', end='')
                    for tn in n.tree.get_data():
                        print(repr(tn), end=" || ")
                    print(')', end='')
                elif not n.gn.is_choice:
                    print(repr(n.gn.node), end=" || ")
        print('')
        return

    M = TreeSearchMemoTree()
    M.load_from_file()

    stime = time.time()
    sentence_tree = find_bf(bf, memo= M)
    if show_time:
        print(time.time()-stime)

    if show_leaves:
        print(' '.join([tree_to_leafs(tree) for tree in sentence_tree.get_data()]))

    if show_trees:
        for tree in sentence_tree.get_data():
            print(tree)
            print('')

    words = '. '.join([tree_to_words(tree) for tree in sentence_tree.get_data()])


    # Write words to output file if specified, otherwise print it
    if output_file:
        with open(output_file, "w") as f:
            f.write(words)
        print(f"Output written to {output_file}")
    else:
        print(words)

def update_memo_table():
    M = TreeSearchMemoTree()
    M.load_from_file()
    yes = ['y', 'yes']

    print(M)

    y = input("Update the memo table? (y/n): ").lower().strip()
    if y in yes:
        M.update()

    y = input("Delete entries from the memo table? (y/n): ").lower().strip()
    if y in yes:
        M.delete()

def do_choice_search(graph_search=False):
    if graph_search:
        gs_choice_search()
    else:
        choice_search()

def show_memo_table(filename):
    filename = '.'.join(filename.split('.')[:-1]) + '.pkl'
    print(f"Showing memo table from file: {filename}")

    M = TreeSearchMemoTree()
    M.load_from_file(filename)

    print(M)

def main():

    GENERATE_COMMAND = 'make_love'
    commands = {GENERATE_COMMAND, "update_memo_table", "choice_search", "show_memo_table"}

    # default to generate command if not provided
    if len(sys.argv) >= 2:
        has_command = False
        for command in commands:
            if command in sys.argv:
                has_command = True
                break
        if not has_command:
            sys.argv.insert(1, GENERATE_COMMAND)


    parser = argparse.ArgumentParser(
        description="Love Languages\n\nCommands:\n"
                    f"  [{GENERATE_COMMAND}]      Generate syntax structure from bf program (default command).\n"
                    "  update_memo_table  Update memo table\n"
                    "  choice_search      Choice search (showcases how generation work)\n"
                    "  show_memo_table    Show memo table entries (optional filename, default: ts_memo.pkl)",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Global optional arguments (mainly used by generate)

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', metavar="COMMAND", help="Available commands")

    gen_parser = subparsers.add_parser(GENERATE_COMMAND, help="Convert a bf program (file, argument, or user input) into an equivalent syntax structure")
    gen_parser.add_argument('-o', '--output', help=f"Output file for {GENERATE_COMMAND} command", default=None)
    gen_parser.add_argument('--graph-search', action='store_true', help="Use 'graph search' generation backend (default 'tree search')")
    gen_parser.add_argument('-t', '--show-trees', action='store_true', help="Show syntax trees")
    gen_parser.add_argument('-l', '--show-leaves', action='store_true', help="Show leaves of syntrax trees")
    gen_parser.add_argument('--show-time', action='store_true', help="Show debug timing information")
    gen_parser.add_argument('input_program', nargs='?', help="Input bf program or file path to bf program")

    # update_memo_table command
    subparsers.add_parser('update_memo_table', help="Update the memo table")

    # choice_search command
    choice_parser = subparsers.add_parser('choice_search', help="Execute choice search")
    choice_parser.add_argument('--graph-search', action='store_true', help="Use 'graph search' generation backend (default 'tree search')")

    # show_memo_table command with an optional filename argument
    show_memo_parser = subparsers.add_parser('show_memo_table', help="Print the memo table")
    show_memo_parser.add_argument('filename', nargs='?', default='ts_trees.pkl', help="Memo table file (default: ts_trees.pkl)")


    args = parser.parse_args()

    # Determine which command to run based on arguments.
    if args.command == GENERATE_COMMAND:
        generate(
            input_token=args.input_program,
            output_file=args.output,
            graph_search=args.graph_search,
            show_trees=args.show_trees,
            show_leaves=args.show_leaves,
            show_time=args.show_time
        )
    elif args.command == 'update_memo_table':
        update_memo_table()
    elif args.command == 'choice_search':
        do_choice_search(graph_search=args.graph_search)
    elif args.command == 'show_memo_table':
        show_memo_table(args.filename)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

