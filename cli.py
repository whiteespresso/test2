# coding=utf-8
import argparse

import main


def get_parser():
    """
    Tworzy parser parametrów z linii komend.

    :return: obiekt parsera
    """
    parser = argparse.ArgumentParser(description='Website classificator')
    subparsers = parser.add_subparsers(help='commands')
    classify_parser = subparsers.add_parser('classify')
    classify_parser.add_argument('url')
    classify_parser.add_argument('-f', default="websites.txt")
    classify_parser.add_argument('--retrain', action='store_true')
    classify_parser.set_defaults(func=classify)

    accuracy_parser = subparsers.add_parser('accuracy')
    accuracy_parser.add_argument('partition', type=float)
    accuracy_parser.add_argument('-f', default="websites.txt")
    accuracy_parser.set_defaults(func=accuracy)

    xval_parser = subparsers.add_parser('xval')
    xval_parser.add_argument('folds', type=int)
    xval_parser.add_argument('-f', default="websites.txt")
    xval_parser.set_defaults(func=cross_val)

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('url')
    update_parser.add_argument('category')
    update_parser.set_defaults(func=update)
    return parser


def classify(args):
    """
    Zwraca wynik klasyfikacji.

    :param args: argumenty z linii komend
    """
    print main.classify_website(args.url, force=args.retrain, filename=args.f)


def accuracy(args):
    """
    Zwraca stosunek poprawnie sklasyfikowanych wpisów do pełnej ich liczby.

    :param args: argumenty z linii komend
    """
    print main.get_accuracy(args.partition, args.f)


def cross_val(args):
    """
    Zwraca wynik walidacji krzyżowej.

    :param args: argumenty z linii komend
    """
    print main.get_cross_val(args.folds, args.f)


def update(args):
    """
    Dokonuje douczania klasyfikatora.

    :param args: argumenty z linii komend
    """
    print main.update_website(args.url, args.category)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)
