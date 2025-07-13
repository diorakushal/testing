import streamlit_authenticator as stauth

# Add your plain-text passwords here
passwords = ['123']  

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Print them to copy into your main app
print(hashed_passwords)
