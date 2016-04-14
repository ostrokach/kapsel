# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2016, Continuum Analytics, Inc. All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from __future__ import absolute_import, print_function

from anaconda_project.commands.variable_commands import main
from anaconda_project.internal.test.tmpfile_utils import with_directory_contents
from anaconda_project.project_file import DEFAULT_PROJECT_FILENAME


class Args(object):
    def __init__(self, action, vars_to_add=None, vars_to_remove=None, project='.'):
        self.project = project
        self.action = action
        self.vars_to_add = vars_to_add
        self.vars_to_remove = vars_to_remove


def test_add_variable_command(monkeypatch):

    params = []

    def mock_add_variables(project, _vars):
        params.append(_vars)
        return True

    monkeypatch.setattr('anaconda_project.project_ops.add_variables', mock_add_variables)

    args = Args('add', vars_to_add=['foo=bar', 'baz=qux', 'has_two_equals=foo=bar'])
    res = main(args)
    assert res == 0
    assert [('foo', 'bar'), ('baz', 'qux'), ('has_two_equals', 'foo=bar')] == params[0]


def test_add_variable_project_problem(capsys):
    def check_problem(dirname):
        args = Args('add', vars_to_add=['foo=bar', 'baz=qux'], project=dirname)
        res = main(args)
        assert res == 1

    with_directory_contents({DEFAULT_PROJECT_FILENAME: ("variables:\n" "  42")}, check_problem)

    out, err = capsys.readouterr()
    assert out == ''
    expected_err = ('Unable to load project:\n  '
                    'variables section contains wrong value type 42, should be dict or list of requirements\n')
    assert err == expected_err


def test_add_variable_command_bad(monkeypatch, capsys):

    params = []

    def mock_add_variables(project, _vars):
        params.append(_vars)
        return True

    monkeypatch.setattr('anaconda_project.project_ops.add_variables', mock_add_variables)

    args = Args('add', vars_to_add=['foo=bar', 'baz'])
    res = main(args)
    assert res == 1
    out, err = capsys.readouterr()
    assert "Error: {} doesn't define a name=value pair".format('baz') in out

    assert len(params) == 0


def test_remove_variable_command(monkeypatch):
    params = []

    def check_remove_variable(dirname):
        def mock_remove_variables(project, _vars):
            params.append(_vars)
            return True

        monkeypatch.setattr('anaconda_project.project_ops.remove_variables', mock_remove_variables)
        args = Args('remove', vars_to_remove=['foo', 'baz'], project=dirname)
        res = main(args)
        assert res == 0
        assert len(params) == 1

    with_directory_contents(
        {DEFAULT_PROJECT_FILENAME: ("variables:\n"
                                    "  foo: {default: test}\n"
                                    "  baz: {default: bar}")}, check_remove_variable)


def test_remove_variable_project_problem(monkeypatch):
    def check_problem_remove(dirname):
        args = Args('remove', vars_to_remove=['foo', 'baz'], project=dirname)
        res = main(args)
        assert res == 1

    with_directory_contents({DEFAULT_PROJECT_FILENAME: ("variables:\n" "  foo: true")}, check_problem_remove)
