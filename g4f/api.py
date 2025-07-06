# Make sure this code is inside the async def generate_image(...):
@self.app.post("/v1/images/generate", responses=responses)
async def generate_image(
    request: Request,
    config: ImageGenerationConfig,
    provider: str = None,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(Api.security)] = None
):
    if config.provider is None:
        config.provider = provider
    if config.provider is None:
        config.provider = AppConfig.media_provider
    if config.api_key is None and credentials is not None and credentials.credentials != "secret":
        config.api_key = credentials.credentials
    try:
        # Prepare kwargs for the provider
        provider_kwargs = config.dict(exclude_none=True)
        # If reference_image is present, add it to media as expected by Together
        if getattr(config, 'reference_image', None):
            provider_kwargs["media"] = [[config.reference_image, "reference.png"]]
        response = await self.client.images.generate(
            **provider_kwargs,
        )
        for image in response.data:
            if hasattr(image, "url") and image.url.startswith("/"):
                image.url = f"{request.base_url}{image.url.lstrip('/')}"
        return response
    except (ModelNotFoundError, ProviderNotFoundError) as e:
        logger.exception(e)
        return ErrorResponse.from_exception(e, config, HTTP_404_NOT_FOUND)
    except MissingAuthError as e:
        logger.exception(e)
        return ErrorResponse.from_exception(e, config, HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.exception(e)
        return ErrorResponse.from_exception(e, config, HTTP_500_INTERNAL_SERVER_ERROR) 