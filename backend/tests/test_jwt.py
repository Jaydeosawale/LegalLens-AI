from auth.jwt import JWTService

token = JWTService.create_access_token(
    {
        "sub": "jaydeo@gmail.com"
    }
)

print("\nGenerated Token:\n")
print(token)

print("\nDecoded Payload:\n")
print(JWTService.verify_access_token(token))