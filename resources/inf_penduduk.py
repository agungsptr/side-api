from flask import Blueprint
from flask_restful import Resource, reqparse, fields, marshal

from .resource import *

ip_fields = {
    'id': fields.Integer,
    'total_pria': fields.Integer,
    'total_wanita': fields.Integer,
    'total_kk': fields.Integer,
    'total_rtm': fields.Integer
}


def counter():
    try:
        val = models.InfPenduduk.select().count()
    except models.InfPenduduk.DoesNotExist:
        abort(404)
    else:
        return val


def get_or_abort(id):
    try:
        query = models.InfPenduduk.get_by_id(id)
    except models.InfPenduduk.DoesNotExist:
        abort(404)
    else:
        return query


class BaseIp(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super().__init__()

    def reqargs(self):
        self.reqparse.add_argument(
            'total_pria', type=int,
            required=False, location=['form', 'json'])
        self.reqparse.add_argument(
            'total_wanita', type=int,
            required=False, location=['form', 'json'])
        self.reqparse.add_argument(
            'total_kk', type=int,
            required=False, location=['form', 'json'])
        self.reqparse.add_argument(
            'total_rtm', type=int,
            required=False, location=['form', 'json'])


class GetPost(BaseIp):
    # index
    # @login_required
    def get(self):
        ip = [marshal(ip, ip_fields)
              for ip in models.InfPenduduk.select()]
        return {'success': True,
                'data': ip}

    # store
    # @login_required
    def post(self):
        if counter() >= 1:
            abort(400, "Data can only be created once, please edit as an alternative")

        self.reqargs()
        args = self.reqparse.parse_args()

        try:
            ip = models.InfPenduduk.create(**args)
            return {'success': True,
                    'data': marshal(ip, ip_fields)}
        except models.InfPenduduk.DoesNotExist:
            return {'success': False,
                    'message': 'Model does not exist'}


class GetPutDel(BaseIp):
    # show
    # @login_required
    def get(self, id):
        ip = get_or_abort(id)
        return {'success': True,
                'data': marshal(ip, ip_fields)}

    # edit
    # @login_required
    def put(self, id):
        self.reqargs()

        get_or_abort(id)
        args = self.reqparse.parse_args()

        try:
            models.InfPenduduk.update(**args).where(models.InfPenduduk.id == id).execute()
            return {'success': True,
                    'data': marshal(get_or_abort(id), ip_fields)}
        except models.InfPenduduk.DoesNotExist:
            return {'success': False,
                    'message': 'Model does not exist'}

    # delete
    # @login_required
    def delete(self, id):
        get_or_abort(id)
        models.InfPenduduk.delete().where(models.InfPenduduk.id == id).execute()
        return {'success': True,
                'message': "Info Peduduk Desa is deleted"}


inf_penduduk_api = Blueprint('resources.inf_penduduk', __name__)
api = Api(inf_penduduk_api)
api.add_resource(GetPost, '/inf-penduduk', endpoint='inf-penduduk/gp')
api.add_resource(GetPutDel, '/inf-penduduk/<int:id>', endpoint='inf-penduduk/gpd')
