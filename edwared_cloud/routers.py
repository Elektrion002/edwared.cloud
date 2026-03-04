# edwared_cloud/routers.py
class ClientDatabaseRouter:
    """
    Un enrutador para controlar todas las operaciones de base de datos
    sobre modelos de las aplicaciones de los clientes.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'panaderia':
            return 'panaderia'
        elif model._meta.app_label == 'flores':
            return 'flores'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'panaderia':
            return 'panaderia'
        elif model._meta.app_label == 'flores':
            return 'flores'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir relaciones si ambos objetos están en la misma base de datos
        if obj1._state.db == obj2._state.db:
            return True
        # No permitir relaciones entre bases de datos diferentes
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'panaderia':
            return db == 'panaderia'
        elif app_label == 'flores':
            return db == 'flores'
        elif db in ['panaderia', 'flores']:
            return False
        return db == 'default'
