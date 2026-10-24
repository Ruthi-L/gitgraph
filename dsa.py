from collections import deque

class GitHubGraphDSA:
    def __init__(self, users, relationships):
        """
        Builds an adjacency list representation from SQLite data.
        Users: list of dicts [{'id': 1, 'username': 'octocat'}, ...]
        Relationships: list of dicts [{'follower_name': '...', 'followed_name': '...', 'relation_type': '...'}, ...]
        """
        self.adj_list = {user['username']: [] for user in users}
        self.user_map_lower = {user['username'].lower(): user['username'] for user in users}
        
        # Populate adjacency list (treating graph as undirected/bidirectional for component analysis, 
        # or directed depending on traversal needs)
        for rel in relationships:
            u = rel['follower_name']
            v = rel['followed_name']
            if u not in self.adj_list:
                self.adj_list[u] = []
            if v not in self.adj_list:
                self.adj_list[v] = []
            
            # Avoid duplicate edges in adjacency list
            if v not in self.adj_list[u]:
                self.adj_list[u].append(v)
            if u not in self.adj_list[v]:
                self.adj_list[v].append(u)

    def bfs_shortest_path(self, start_user, target_user):
        """
        Custom BFS Shortest Path algorithm finding the minimum hops between two developers.
        Returns a list of usernames representing the path, or empty list if no path exists.
        """
        start_lower = start_user.lower()
        target_lower = target_user.lower()
        
        # Resolve casing
        start = self.user_map_lower.get(start_lower)
        target = self.user_map_lower.get(target_lower)
        
        if not start or not target or start not in self.adj_list or target not in self.adj_list:
            return []

        queue = deque([[start]])
        visited = {start}

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node.lower() == target_lower:
                return path

            for neighbor in self.adj_list.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []

    def find_connected_components(self):
        """
        Custom Connected Components algorithm using BFS.
        Groups developer profiles into isolated clusters/communities.
        """
        visited = set()
        components = []

        for node in self.adj_list:
            if node not in visited:
                component = []
                queue = deque([node])
                visited.add(node)

                while queue:
                    curr = queue.popleft()
                    component.append(curr)

                    for neighbor in self.adj_list.get(curr, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)

        # Sort components by size descending (largest developer clusters first)
        components.sort(key=len, reverse=True)
        return components