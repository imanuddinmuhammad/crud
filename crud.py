import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- Global Data Storage (In-memory DataFrames & Users) ---
# In a real app, these would be persisted in a database (e.g., SQLite, PostgreSQL)

# --- Initial User Data (Hardcoded for demonstration) ---
# In a real app, this would be hashed passwords and proper user management
HARDCODED_USERS = {
    "superadmin@mail.com": {"password": "superpassword", "role": "Super Admin", "company": "Global"},
    "admin1@companyA.com": {"password": "adminpasswordA", "role": "Admin", "company": "Company A"},
    "user1@companyA.com": {"password": "userpasswordA", "role": "User", "company": "Company A"},
    "admin2@companyB.com": {"password": "adminpasswordB", "role": "Admin", "company": "Company B"},
    "user2@companyB.com": {"password": "userpasswordB", "role": "User", "company": "Company B"},
}

# --- Initialize Session State for DataFrames and Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.session_state.user_company = None

if 'users_df' not in st.session_state:
    st.session_state.users_df = pd.DataFrame(
        columns=['id', 'name', 'email', 'company', 'role']
    )
    # Add initial users from HARDCODED_USERS (simulate database init)
    for email, details in HARDCODED_USERS.items():
        st.session_state.users_df.loc[len(st.session_state.users_df)] = {
            'id': str(uuid.uuid4()),
            'name': email.split('@')[0].capitalize(),
            'email': email,
            'company': details['company'],
            'role': details['role']
        }

if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame(
        columns=['id', 'product_name', 'price', 'stock', 'company']
    )
    st.session_state.products_df.loc[len(st.session_state.products_df)] = {'id': str(uuid.uuid4()), 'product_name': 'Laptop A', 'price': 1200.00, 'stock': 50, 'company': 'Company A'}
    st.session_state.products_df.loc[len(st.session_state.products_df)] = {'id': str(uuid.uuid4()), 'product_name': 'Mouse A', 'price': 25.50, 'stock': 200, 'company': 'Company A'}
    st.session_state.products_df.loc[len(st.session_state.products_df)] = {'id': str(uuid.uuid4()), 'product_name': 'Server B', 'price': 5000.00, 'stock': 10, 'company': 'Company B'}
    st.session_state.products_df.loc[len(st.session_state.products_df)] = {'id': str(uuid.uuid4()), 'product_name': 'Keyboard B', 'price': 75.00, 'stock': 150, 'company': 'Company B'}


# Product Request Statuses: 'Pending', 'Approved', 'Rejected'
if 'product_requests_df' not in st.session_state:
    st.session_state.product_requests_df = pd.DataFrame(
        columns=['request_id', 'product_id', 'request_type', 'old_data', 'new_data', 'requested_by_email', 'status', 'admin_notes', 'request_date', 'approval_date']
    )


# --- Authentication Functions ---
def authenticate(email, password):
    if email in HARDCODED_USERS and HARDCODED_USERS[email]['password'] == password:
        st.session_state.logged_in = True
        st.session_state.current_user = email
        st.session_state.user_role = HARDCODED_USERS[email]['role']
        st.session_state.user_company = HARDCODED_USERS[email]['company']
        st.success(f"Welcome, {st.session_state.user_role} from {st.session_state.user_company}!")
        # CHANGE THIS LINE:
        st.rerun() # Rerun to show the main app
    else:
        st.error("Invalid email or password.")

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.session_state.user_company = None
    st.info("Logged out successfully.")
    st.experimental_rerun()

# --- Helper Functions for Data Manipulation ---

def add_record(df_name, new_data):
    """Adds a new record to the specified DataFrame."""
    df = st.session_state[df_name]
    new_data['id'] = str(uuid.uuid4()) # Generate unique ID
    new_df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    st.session_state[df_name] = new_df
    st.success(f"Record added successfully!")

def update_record(df_name, record_id, updated_data):
    """Updates an existing record in the specified DataFrame."""
    df = st.session_state[df_name]
    if record_id in df['id'].values:
        idx = df[df['id'] == record_id].index[0]
        for key, value in updated_data.items():
            st.session_state[df_name].at[idx, key] = value
        st.success("Record updated successfully!")
    else:
        st.error("Record not found.")

def delete_record(df_name, record_id):
    """Deletes a record from the specified DataFrame."""
    df = st.session_state[df_name]
    initial_rows = len(df)
    st.session_state[df_name] = df[df['id'] != record_id].reset_index(drop=True)
    if len(st.session_state[df_name]) < initial_rows:
        st.success("Record deleted successfully!")
    else:
        st.error("Record not found or could not be deleted.")


# --- CRUD UI Functions for Users ---

def user_crud_ui():
    st.header("👥 User Management")

    current_user_role = st.session_state.user_role
    current_user_company = st.session_state.user_company

    # Filter users based on company and role
    if current_user_role == "Super Admin":
        display_df = st.session_state.users_df.copy()
    else: # Admin can only see users from their company
        display_df = st.session_state.users_df[st.session_state.users_df['company'] == current_user_company].copy()

    st.subheader("Current Users")
    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No users found for your company.")

    st.markdown("---")

    # Only Super Admin and Admin can add/update/delete users (with restrictions for Admin)
    if current_user_role in ["Super Admin", "Admin"]:
        tab1, tab2, tab3 = st.tabs(["➕ Add User", "✏️ Update User", "🗑️ Delete User"])

        with tab1:
            st.subheader("Add New User")
            # Admin cannot create Super Admins or other Admins
            allowed_roles_for_creation = ["User"]
            if current_user_role == "Super Admin":
                allowed_roles_for_creation = ["User", "Admin", "Super Admin"]
            
            # Admin can only create users for their company
            if current_user_role == "Admin":
                st.info(f"You can only add users to your company: **{current_user_company}**")
            
            with st.form("add_user_form", clear_on_submit=True):
                name = st.text_input("Name", key="add_user_name")
                email = st.text_input("Email", key="add_user_email")
                
                # Company selection: Super Admin can choose, Admin is fixed
                if current_user_role == "Super Admin":
                    company = st.selectbox("Company", options=list(st.session_state.users_df['company'].unique()) + ["New Company"], key="add_user_company")
                    if company == "New Company":
                        company = st.text_input("Enter New Company Name", key="new_company_name").strip()
                else: # Admin
                    company = current_user_company
                    st.text_input("Company (fixed for your role)", value=company, disabled=True)

                role = st.selectbox("Role", allowed_roles_for_creation, key="add_user_role")
                password = st.text_input("Temporary Password", type="password", key="add_user_password")
                
                submitted = st.form_submit_button("Add User")
                if submitted:
                    if name and email and company and role and password:
                        if email in HARDCODED_USERS:
                            st.warning("User with this email already exists.")
                        else:
                            # Add to in-memory HARDCODED_USERS for login simulation
                            HARDCODED_USERS[email] = {"password": password, "role": role, "company": company}
                            add_record('users_df', {'name': name, 'email': email, 'company': company, 'role': role})
                            st.experimental_rerun()
                    else:
                        st.warning("Please fill in all fields.")

        with tab2:
            st.subheader("Update Existing User")
            if not display_df.empty:
                # Filter selectable users for update: Admin cannot edit other admins/superadmins
                if current_user_role == "Admin":
                    updatable_users = display_df[~display_df['role'].isin(["Admin", "Super Admin"])]
                else: # Super Admin can update anyone
                    updatable_users = display_df

                user_options = updatable_users.apply(lambda row: f"{row['name']} ({row['email']})", axis=1).tolist()
                user_ids_map = {f"{row['name']} ({row['email']})": row['id'] for _, row in updatable_users.iterrows()}

                selected_user_option = st.selectbox("Select User to Update", [""] + user_options, key="update_user_select")
                selected_user_id = user_ids_map.get(selected_user_option)

                if selected_user_id:
                    current_user_data = st.session_state.users_df[st.session_state.users_df['id'] == selected_user_id].iloc[0]
                    with st.form("update_user_form"):
                        updated_name = st.text_input("Name", value=current_user_data['name'], key="update_user_name")
                        updated_email = st.text_input("Email", value=current_user_data['email'], key="update_user_email", disabled=True) # Email usually not editable
                        
                        # Company: Super Admin can change, Admin is fixed
                        if current_user_role == "Super Admin":
                            updated_company = st.selectbox("Company", options=list(st.session_state.users_df['company'].unique()), index=list(st.session_state.users_df['company'].unique()).index(current_user_data['company']), key="update_user_company")
                        else:
                            updated_company = current_user_data['company']
                            st.text_input("Company (fixed for your role)", value=updated_company, disabled=True)

                        # Role: Admin cannot change role of other admins/superadmins, and cannot promote to Admin/Super Admin
                        allowed_roles_for_update = ["User"]
                        if current_user_role == "Super Admin":
                            allowed_roles_for_update = ["User", "Admin", "Super Admin"]
                        elif current_user_role == "Admin" and current_user_data['role'] == "User": # Admin can change their own user's role if it's 'User'
                             allowed_roles_for_update = ["User"] # Admin can only keep it as User

                        updated_role = st.selectbox("Role", allowed_roles_for_update, index=allowed_roles_for_update.index(current_user_data['role']) if current_user_data['role'] in allowed_roles_for_update else 0, key="update_user_role")
                        
                        update_submitted = st.form_submit_button("Update User")
                        if update_submitted:
                            updated_data = {
                                'name': updated_name,
                                'company': updated_company,
                                'role': updated_role
                            }
                            update_record('users_df', selected_user_id, updated_data)
                            # Update HARDCODED_USERS as well for login consistency
                            HARDCODED_USERS[current_user_data['email']]['role'] = updated_role
                            HARDCODED_USERS[current_user_data['email']]['company'] = updated_company
                            st.experimental_rerun()
                else:
                    st.info("No user selected to update.")
            else:
                st.info("No users to update.")

        with tab3:
            st.subheader("Delete User")
            if not display_df.empty:
                # Filter selectable users for deletion: Admin cannot delete other admins/superadmins
                if current_user_role == "Admin":
                    deletable_users = display_df[~display_df['role'].isin(["Admin", "Super Admin"])]
                else: # Super Admin can delete anyone except themselves
                    deletable_users = display_df[display_df['email'] != st.session_state.current_user] # Cannot delete self

                user_options = deletable_users.apply(lambda row: f"{row['name']} ({row['email']})", axis=1).tolist()
                user_ids_map = {f"{row['name']} ({row['email']})": row['id'] for _, row in deletable_users.iterrows()}

                selected_user_option_delete = st.selectbox("Select User to Delete", [""] + user_options, key="delete_user_select")
                selected_user_id_delete = user_ids_map.get(selected_user_option_delete)

                if st.button("Delete User", key="delete_user_button"):
                    if selected_user_id_delete:
                        # Find the email of the user to delete
                        email_to_delete = st.session_state.users_df[st.session_state.users_df['id'] == selected_user_id_delete]['email'].iloc[0]
                        
                        delete_record('users_df', selected_user_id_delete)
                        # Remove from HARDCODED_USERS as well
                        if email_to_delete in HARDCODED_USERS:
                            del HARDCODED_USERS[email_to_delete]
                        st.experimental_rerun()
                    else:
                        st.warning("Please select a user to delete.")
            else:
                st.info("No users to delete.")
    else:
        st.warning("You do not have permission to manage users.")


# --- CRUD UI Functions for Products ---

def product_crud_ui():
    st.header("📦 Product Management")

    current_user_role = st.session_state.user_role
    current_user_company = st.session_state.user_company

    # Filter products based on company
    if current_user_role == "Super Admin":
        display_df = st.session_state.products_df.copy()
    else: # Admin/User can only see products from their company
        display_df = st.session_state.products_df[st.session_state.products_df['company'] == current_user_company].copy()

    st.subheader("Current Products")
    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No products found for your company.")

    st.markdown("---")

    # Tabs depending on role
    if current_user_role in ["Super Admin", "Admin"]:
        tab1, tab2, tab3 = st.tabs(["➕ Add Product", "✏️ Update Product", "🗑️ Delete Product"])
    else: # User role can only propose changes
        tab1, tab2 = st.tabs(["✏️ Propose Product Update", "🗑️ Propose Product Deletion"])


    # --- Add Product (Admin/Super Admin only) ---
    if current_user_role in ["Super Admin", "Admin"]:
        with tab1: # Add Product Tab
            st.subheader("Add New Product")
            with st.form("add_product_form", clear_on_submit=True):
                product_name = st.text_input("Product Name", key="add_product_name")
                price = st.number_input("Price", min_value=0.01, format="%.2f", key="add_product_price")
                stock = st.number_input("Stock", min_value=0, step=1, key="add_product_stock")
                
                if current_user_role == "Super Admin":
                    company = st.selectbox("Company", options=list(st.session_state.products_df['company'].unique()) + ["New Company"], key="add_product_company")
                    if company == "New Company":
                        company = st.text_input("Enter New Company Name for Product", key="new_product_company_name").strip()
                else: # Admin
                    company = current_user_company
                    st.text_input("Company (fixed for your role)", value=company, disabled=True)

                submitted = st.form_submit_button("Add Product")
                if submitted:
                    if product_name and price is not None and stock is not None and company:
                        add_record('products_df', {'product_name': product_name, 'price': price, 'stock': stock, 'company': company})
                        st.experimental_rerun()
                    else:
                        st.warning("Please fill in all fields.")

    # --- Update/Propose Update Product ---
    update_tab_index = 1 if current_user_role in ["Super Admin", "Admin"] else 0
    with st.tabs([""] * 3 if current_user_role in ["Super Admin", "Admin"] else [""] * 2)[update_tab_index]: # Access the correct tab
        st.subheader("Update Existing Product" if current_user_role in ["Super Admin", "Admin"] else "Propose Product Update")
        if not display_df.empty:
            product_options = display_df.apply(lambda row: f"{row['product_name']} (ID: {row['id'][-4:]})", axis=1).tolist()
            product_ids_map = {f"{row['product_name']} (ID: {row['id'][-4:]})": row['id'] for _, row in display_df.iterrows()}

            selected_product_option = st.selectbox("Select Product to Update", [""] + product_options, key="update_product_select")
            selected_product_id = product_ids_map.get(selected_product_option)

            if selected_product_id:
                current_product_data = st.session_state.products_df[st.session_state.products_df['id'] == selected_product_id].iloc[0]
                
                with st.form("update_product_form"):
                    updated_product_name = st.text_input("Product Name", value=current_product_data['product_name'], key="update_product_name")
                    updated_price = st.number_input("Price", min_value=0.01, format="%.2f", value=current_product_data['price'], key="update_product_price")
                    updated_stock = st.number_input("Stock", min_value=0, step=1, value=current_product_data['stock'], key="update_product_stock")
                    
                    if current_user_role == "Super Admin":
                        updated_company = st.selectbox("Company", options=list(st.session_state.products_df['company'].unique()), index=list(st.session_state.products_df['company'].unique()).index(current_product_data['company']), key="update_product_company")
                    else:
                        updated_company = current_product_data['company']
                        st.text_input("Company (fixed for your role)", value=updated_company, disabled=True)
                    
                    if current_user_role in ["Super Admin", "Admin"]:
                        update_submitted = st.form_submit_button("Update Product")
                        if update_submitted:
                            updated_data = {
                                'product_name': updated_product_name,
                                'price': updated_price,
                                'stock': updated_stock,
                                'company': updated_company
                            }
                            update_record('products_df', selected_product_id, updated_data)
                            st.experimental_rerun()
                    else: # User proposes update
                        propose_update_submitted = st.form_submit_button("Propose Update")
                        if propose_update_submitted:
                            old_data = current_product_data.to_dict()
                            new_data = {
                                'product_name': updated_product_name,
                                'price': updated_price,
                                'stock': updated_stock,
                                'company': updated_company # Should be same as old data company
                            }
                            # Check if actual changes were made
                            if old_data['product_name'] == new_data['product_name'] and \
                               old_data['price'] == new_data['price'] and \
                               old_data['stock'] == new_data['stock']:
                                st.warning("No changes detected to propose.")
                            else:
                                st.session_state.product_requests_df.loc[len(st.session_state.product_requests_df)] = {
                                    'request_id': str(uuid.uuid4()),
                                    'product_id': selected_product_id,
                                    'request_type': 'Update',
                                    'old_data': old_data,
                                    'new_data': new_data,
                                    'requested_by_email': st.session_state.current_user,
                                    'status': 'Pending',
                                    'admin_notes': '',
                                    'request_date': datetime.now().isoformat(),
                                    'approval_date': ''
                                }
                                st.success("Product update request submitted for approval!")
                                st.experimental_rerun()
            else:
                st.info("No product selected to update.")
        else:
            st.info("No products to update.")

    # --- Delete/Propose Delete Product ---
    delete_tab_index = 2 if current_user_role in ["Super Admin", "Admin"] else 1
    with st.tabs([""] * 3 if current_user_role in ["Super Admin", "Admin"] else [""] * 2)[delete_tab_index]:
        st.subheader("Delete Product" if current_user_role in ["Super Admin", "Admin"] else "Propose Product Deletion")
        if not display_df.empty:
            product_options_delete = display_df.apply(lambda row: f"{row['product_name']} (ID: {row['id'][-4:]})", axis=1).tolist()
            product_ids_map_delete = {f"{row['product_name']} (ID: {row['id'][-4:]})": row['id'] for _, row in display_df.iterrows()}

            selected_product_option_delete = st.selectbox("Select Product to Delete", [""] + product_options_delete, key="delete_product_select")
            selected_product_id_delete = product_ids_map_delete.get(selected_product_option_delete)

            if current_user_role in ["Super Admin", "Admin"]:
                if st.button("Delete Product", key="delete_product_button"):
                    if selected_product_id_delete:
                        delete_record('products_df', selected_product_id_delete)
                        st.experimental_rerun()
                    else:
                        st.warning("Please select a product to delete.")
            else: # User proposes delete
                if st.button("Propose Deletion", key="propose_delete_button"):
                    if selected_product_id_delete:
                        # Ensure the product exists before proposing deletion
                        if selected_product_id_delete in st.session_state.products_df['id'].values:
                            product_to_delete_data = st.session_state.products_df[st.session_state.products_df['id'] == selected_product_id_delete].iloc[0].to_dict()
                            st.session_state.product_requests_df.loc[len(st.session_state.product_requests_df)] = {
                                'request_id': str(uuid.uuid4()),
                                'product_id': selected_product_id_delete,
                                'request_type': 'Delete',
                                'old_data': product_to_delete_data,
                                'new_data': {}, # No new data for delete
                                'requested_by_email': st.session_state.current_user,
                                'status': 'Pending',
                                'admin_notes': '',
                                'request_date': datetime.now().isoformat(),
                                'approval_date': ''
                            }
                            st.success("Product deletion request submitted for approval!")
                            st.experimental_rerun()
                        else:
                            st.error("Selected product not found.")
                    else:
                        st.warning("Please select a product to propose deletion.")
        else:
            st.info("No products to delete.")


# --- Approval Workflow UI (Admin/Super Admin only) ---
def approval_workflow_ui():
    st.header("📝 Product Approval Workflow")

    current_user_role = st.session_state.user_role
    current_user_company = st.session_state.user_company

    # Filter requests based on role and company
    if current_user_role == "Super Admin":
        pending_requests = st.session_state.product_requests_df[
            st.session_state.product_requests_df['status'] == 'Pending'
        ].copy()
    else: # Admin can only see requests for their company's products
        # Get product IDs associated with the admin's company
        company_product_ids = st.session_state.products_df[
            st.session_state.products_df['company'] == current_user_company
        ]['id'].tolist()
        
        pending_requests = st.session_state.product_requests_df[
            (st.session_state.product_requests_df['status'] == 'Pending') &
            (st.session_state.product_requests_df['product_id'].isin(company_product_ids))
        ].copy()


    if not pending_requests.empty:
        st.subheader("Pending Product Requests")
        st.dataframe(pending_requests[['request_id', 'product_id', 'request_type', 'requested_by_email', 'request_date']], use_container_width=True)

        st.markdown("---")

        request_options = pending_requests.apply(lambda row: f"{row['request_type']} for {row['product_id'][-4:]} by {row['requested_by_email']}", axis=1).tolist()
        request_ids_map = {opt: req_id for opt, req_id in zip(request_options, pending_requests['request_id'].tolist())}

        selected_request_option = st.selectbox("Select Request to Review", [""] + request_options, key="select_request_to_review")
        selected_request_id = request_ids_map.get(selected_request_option)

        if selected_request_id:
            request_data = pending_requests[pending_requests['request_id'] == selected_request_id].iloc[0]
            st.subheader(f"Review Request: {request_data['request_type']} - Product ID: {request_data['product_id'][-4:]}")
            st.write(f"**Requested by:** {request_data['requested_by_email']}")
            st.write(f"**Request Date:** {datetime.fromisoformat(request_data['request_date']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Request Type:** {request_data['request_type']}")

            if request_data['request_type'] == 'Update':
                st.write("**Old Data:**")
                st.json(request_data['old_data'])
                st.write("**New Data Proposed:**")
                st.json(request_data['new_data'])
            elif request_data['request_type'] == 'Delete':
                st.write("**Product to be deleted (Old Data):**")
                st.json(request_data['old_data'])

            admin_notes = st.text_area("Admin Notes/Reason (for rejection):", key="admin_approval_notes")

            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button("Approve Request", key="approve_request_button"):
                    if request_data['request_type'] == 'Update':
                        update_record('products_df', request_data['product_id'], request_data['new_data'])
                    elif request_data['request_type'] == 'Delete':
                        delete_record('products_df', request_data['product_id'])
                    
                    # Update request status
                    req_idx = st.session_state.product_requests_df[st.session_state.product_requests_df['request_id'] == selected_request_id].index[0]
                    st.session_state.product_requests_df.at[req_idx, 'status'] = 'Approved'
                    st.session_state.product_requests_df.at[req_idx, 'admin_notes'] = admin_notes
                    st.session_state.product_requests_df.at[req_idx, 'approval_date'] = datetime.now().isoformat()
                    st.success("Request Approved and Product Data Updated!")
                    st.experimental_rerun()
            with col_reject:
                if st.button("Reject Request", key="reject_request_button"):
                    if admin_notes:
                        req_idx = st.session_state.product_requests_df[st.session_state.product_requests_df['request_id'] == selected_request_id].index[0]
                        st.session_state.product_requests_df.at[req_idx, 'status'] = 'Rejected'
                        st.session_state.product_requests_df.at[req_idx, 'admin_notes'] = admin_notes
                        st.session_state.product_requests_df.at[req_idx, 'approval_date'] = datetime.now().isoformat()
                        st.warning("Request Rejected!")
                        st.experimental_rerun()
                    else:
                        st.error("Please provide a reason for rejection.")
        else:
            st.info("Select a request to review.")
    else:
        st.info("No pending product requests for your company.")

# --- Main App Logic ---

st.set_page_config(layout="wide", page_title="Advanced Multi-Entity CRUD App")

st.title("🛡️ Secure Multi-Entity CRUD App with RBAC")

# --- Login/Logout UI ---
if not st.session_state.logged_in:
    st.sidebar.header("Login")
    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            authenticate(email, password)
    st.info("Please log in to access the application.")
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.current_user}**")
    st.sidebar.write(f"Role: **{st.session_state.user_role}**")
    st.sidebar.write(f"Company: **{st.session_state.user_company}**")
    if st.sidebar.button("Logout"):
        logout()

    st.sidebar.markdown("---")

    # --- Main Application Menus (after login) ---
    menu_options = []
    if st.session_state.user_role in ["Super Admin", "Admin"]:
        menu_options.append("Users")
    menu_options.append("Products")
    if st.session_state.user_role in ["Super Admin", "Admin"]:
        menu_options.append("Product Approvals")

    if menu_options:
        menu_selection = st.sidebar.radio(
            "Select Entity",
            menu_options
        )

        if menu_selection == "Users":
            user_crud_ui()
        elif menu_selection == "Products":
            product_crud_ui()
        elif menu_selection == "Product Approvals":
            approval_workflow_ui()
    else:
        st.warning("You do not have access to any modules. Please contact your administrator.")

st.sidebar.markdown("---")
st.sidebar.info("This is an in-memory CRUD app. Data will reset on page refresh or app restart.")
st.sidebar.markdown("---")
st.sidebar.subheader("Test Accounts:")
st.sidebar.markdown("""
- **Super Admin:** `superadmin@mail.com` / `superpassword`
- **Company A Admin:** `admin1@companyA.com` / `adminpasswordA`
- **Company A User:** `user1@companyA.com` / `userpasswordA`
- **Company B Admin:** `admin2@companyB.com` / `adminpasswordB`
- **Company B User:** `user2@companyB.com` / `userpasswordB`
""")