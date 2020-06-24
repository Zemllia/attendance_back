from rest_framework.schemas import SchemaGenerator
from rest_framework.schemas.coreapi import LinkNode, insert_into


class CoreAPISchemaGenerator(SchemaGenerator):
    def get_links(self, request=None):
        """
        Return a dictionary containing all the links that should be
        included in the API schema.
        """
        links = LinkNode()
        paths, view_endpoints = self._get_paths_and_endpoints(request)
        # Only generate the path prefix for paths that will be included
        if not paths:
            return None
        prefix = self.determine_path_prefix(paths)
        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue
            schemas = getattr(view, 'schemas', None)
            if schemas and hasattr(view, 'action') and view.action in schemas:
                schema = schemas[view.action]
                schema.view = view
            else:
                schema = view.schema
            link = schema.get_link(path, method, base_url=self.url)
            subpath = path[len(prefix):]
            keys = self.get_keys(subpath, method, view)
            insert_into(links, keys, link)
        return links