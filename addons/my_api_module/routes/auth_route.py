# -*- coding: utf-8 -*-
import json
from odoo import http
from psycopg2 import errors
from psycopg2 import IntegrityError
from odoo.http import request

# local package
from ..authentication.auth_controller import AuthController


class AuthRoute(http.Controller):

    @http.route("/auth_test/register", type="http", auth="public", methods=["POST"], csrf=False)
    def register(self):
        return AuthController('user').register()

    @http.route("/auth_test/login", type="http", auth="public", methods=["POST"], csrf=False)
    def login(self):
        return AuthController('user').login()