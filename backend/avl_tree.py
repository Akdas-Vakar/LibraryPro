class AVLNode:

    def __init__(self, key, value):

        self.key = key  

        self.value = value  

        self.left = None

        self.right = None

        self.height = 1

class AVLTree:

    def __init__(self):

        self.root = None

        self.size = 0

    def _get_height(self, root):

        if not root:

            return 0

        return root.height

    def _get_balance(self, root):

        if not root:

            return 0

        return self._get_height(root.left) - self._get_height(root.right)

    def _right_rotate(self, z):

        y = z.left

        T3 = y.right

        y.right = z

        z.left = T3

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))

        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _left_rotate(self, z):

        y = z.right

        T2 = y.left

        y.left = z

        z.right = T2

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))

        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def insert(self, key, value):

        if key is None or str(key).strip() == '':

            return 

        self.root = self._insert(self.root, str(key).strip(), value)

    def _insert(self, root, key, value):

        if not root:

            self.size += 1

            return AVLNode(key, value)

        elif key < root.key:

            root.left = self._insert(root.left, key, value)

        elif key > root.key:

            root.right = self._insert(root.right, key, value)

        else:

            root.value = value

            return root

        root.height = 1 + max(self._get_height(root.left), self._get_height(root.right))

        balance = self._get_balance(root)

        if balance > 1 and key < root.left.key:

            return self._right_rotate(root)

        if balance < -1 and key > root.right.key:

            return self._left_rotate(root)

        if balance > 1 and key > root.left.key:

            root.left = self._left_rotate(root.left)

            return self._right_rotate(root)

        if balance < -1 and key < root.right.key:

            root.right = self._right_rotate(root.right)

            return self._left_rotate(root)

        return root

    def delete(self, key):

        if key is None or str(key).strip() == '':

            return

        self.root = self._delete(self.root, str(key).strip())

    def _delete(self, root, key):

        if not root:

            return root

        if key < root.key:

            root.left = self._delete(root.left, key)

        elif key > root.key:

            root.right = self._delete(root.right, key)

        else:

            if root.left is None:

                temp = root.right

                root = None

                self.size -= 1

                return temp

            elif root.right is None:

                temp = root.left

                root = None

                self.size -= 1

                return temp

            temp = self._get_min_value_node(root.right)

            root.key = temp.key

            root.value = temp.value

            root.right = self._delete(root.right, temp.key)

        if root is None:

            return root

        root.height = 1 + max(self._get_height(root.left), self._get_height(root.right))

        balance = self._get_balance(root)

        if balance > 1 and self._get_balance(root.left) >= 0:

            return self._right_rotate(root)

        if balance > 1 and self._get_balance(root.left) < 0:

            root.left = self._left_rotate(root.left)

            return self._right_rotate(root)

        if balance < -1 and self._get_balance(root.right) <= 0:

            return self._left_rotate(root)

        if balance < -1 and self._get_balance(root.right) > 0:

            root.right = self._right_rotate(root.right)

            return self._left_rotate(root)

        return root

    def _get_min_value_node(self, root):

        if root is None or root.left is None:

            return root

        return self._get_min_value_node(root.left)

    def search(self, key):

        if key is None or str(key).strip() == '':

            return None

        node = self._search(self.root, str(key).strip())

        if node:

            return node.value

        return None

    def _search(self, root, key):

        if root is None or root.key == key:

            return root

        if root.key < key:

            return self._search(root.right, key)

        return self._search(root.left, key)

