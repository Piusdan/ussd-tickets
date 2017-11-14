#!/usr/bin/env bash
gunicorn manage:app --reload --workers 2