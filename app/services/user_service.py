from typing import List, Optional, Sequence
from uuid import UUID

from app.database.models import User
from app.email import EmailClient
from app.enums import TemplateHTML
from app.error import UserAlreadyExist, UserNotFound
from app.repositories import InterfaceContractRepository, InterfaceUserRepository
from app.schemas import Contract as ContractDTO
from app.schemas import UserCreate, UserDB

from .security_service import SecurityService


class UserService:
    def __init__(
        self,
        repository: InterfaceUserRepository,
        contract_repository: InterfaceContractRepository,
    ) -> None:
        self.repository: InterfaceUserRepository = repository
        self.contract_repository: InterfaceContractRepository = contract_repository
        self.security_service: SecurityService = SecurityService()

    async def create_user(self, user_create: UserCreate) -> None:
        if await self.repository.get_user_by_email(email=user_create.email):
            raise UserAlreadyExist()

        hashed_password: str = self.security_service.hash_password(
            password=user_create.password
        )

        user: UserCreate = UserCreate(
            password=hashed_password, **user_create.model_dump()
        )

        await self.repository.create_user(user_create=user)

        client: EmailClient = EmailClient()

        # TODO: Crear un modelo para enviar por HTML

        await client.send_email(
            subject="Bienvenido a Studeeo!!",
            email=user_create.email,
            email_information=user_create,
            template_name=TemplateHTML.VERIFICATION,
        )

    async def get_users(self, is_active: bool) -> List[UserDB]:
        users: Sequence[User] = await self.repository.get_users(is_active=is_active)

        return [UserDB.model_validate(user) for user in users]

    async def activate_user(self, id_user: UUID, external_reference: int) -> None:
        user: Optional[User] = await self.repository.get_user(id_user=id_user)

        if not user:
            raise UserNotFound()

        user.activate()

        user.set_external_refence(external_reference=external_reference)

        try:
            await self.repository.update_user(user=user)

            # Llamar al cliente de odoo para obtener su informacion y poblar la base de datos

        except Exception:
            raise

    async def create_contract(
        self, referer_id_user: UUID, referred_id_user: UUID, contract: ContractDTO
    ) -> None:
        user_referenced: Optional[User] = await self.repository.get_user(
            id_user=referred_id_user
        )

        user_referer: Optional[User] = await self.repository.get_user(
            id_user=referer_id_user
        )

        if not user_referenced or not user_referer:
            raise UserNotFound()

        try:
            await self.contract_repository.create_contract(
                referer_id_user=user_referer.id,
                referred_id_user=user_referenced.id,
                percentaje=contract.percentaje,
                valid_from=contract.valid_from,
                valid_to=contract.valid_to,
            )

        except Exception:
            raise
