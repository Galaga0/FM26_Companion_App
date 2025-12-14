 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/streamlit_app.py b/streamlit_app.py
new file mode 100644
index 0000000000000000000000000000000000000000..8e91d8e6c271b59059e61ede7f43ec2d6a18e79c
--- /dev/null
+++ b/streamlit_app.py
@@ -0,0 +1,8 @@
+"""Streamlit entrypoint for FM26 Squad Helper.
+
+Importing the main module runs the Streamlit app as usual.
+"""
+
+import fm26_helper_app
+
+__all__ = ["fm26_helper_app"]
 
EOF
)
