from aws_cdk import (
    aws_cognito as cognito,
    aws_iam as iam,
    CfnOutput,
    Stack
)
from constructs import Construct


class AuthStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the Cognito User Pool
        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name="FunFactsUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
        )

        # Define the Cognito User Pool Client
        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                admin_user_password=True
            ),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=["funfactapp://"],
                logout_urls=["funfactapp://"],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL, cognito.OAuthScope.PROFILE]
            )
        )

        # Define the Cognito Identity Pool
        identity_pool = cognito.CfnIdentityPool(
            self, "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[{
                "clientId": user_pool_client.user_pool_client_id,
                "providerName": user_pool.user_pool_provider_name
            }]
        )

        # Define roles for authenticated and unauthenticated users
        authenticated_role = iam.Role(
            self, "CognitoDefaultAuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={"StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                            "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"}},
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            ),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonCognitoPowerUser")]
        )

        unauthenticated_role = iam.Role(
            self, "CognitoDefaultUnauthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                federated="cognito-identity.amazonaws.com",
                conditions={"StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                            "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "unauthenticated"}},
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            ),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonCognitoReadOnly")]
        )

        cognito.CfnIdentityPoolRoleAttachment(
            self, "DefaultValid",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": authenticated_role.role_arn,
                "unauthenticated": unauthenticated_role.role_arn
            }
        )

        # Output the Cognito details
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "IdentityPoolId", value=identity_pool.ref)
        CfnOutput(self, "CognitoDomain", value=user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="fun-facts-app"
            )
        ).domain_name)
