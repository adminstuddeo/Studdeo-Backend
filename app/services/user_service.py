from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Sequence, Set
from uuid import UUID

from app.configuration import configuration
from app.database.models import User
from app.email import EmailClient
from app.enums import TemplateHTML
from app.error import UserAlreadyExist, UserNotFound
from app.repositories import (
    InterfaceContractRepository,
    InterfaceUserRepository,
    OdooRepository,
)
from app.schemas import Contract as ContractDTO
from app.schemas import (
    ContractCreate,
    TeacherOdoo,
    UserCreate,
    UserCreatedEmail,
    UserDB,
)

from .security_service import SecurityService


@dataclass
class UserService:
    repository: InterfaceUserRepository
    contract_repository: InterfaceContractRepository
    security_service: SecurityService = field(default_factory=SecurityService)
    external_repository: OdooRepository = field(default_factory=OdooRepository)

    async def activate_user(self, id_user: UUID, external_reference: int) -> None:
        user: Optional[User] = await self.repository.get_user(id_user=id_user)

        if not user or user.is_active:
            raise UserNotFound()

        user.activate()

        user.set_external_refence(external_reference=external_reference)

        await self.repository.update_user(user=user)

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

        contract_create = ContractCreate(
            referer_id_user=referer_id_user,
            referred_id_user=referred_id_user,
            **contract.model_dump(),
        )

        await self.contract_repository.create_contract(contract_create=contract_create)

    async def create_user(self, user_create: UserCreate) -> User:
        if await self.repository.get_user_by_email(email=user_create.email) is not None:
            raise UserAlreadyExist()

        hashed_password: str = self.security_service.hash_password(
            password=user_create.password
        )

        user: UserCreate = UserCreate(
            password=hashed_password,
            email=user_create.email,
            name=user_create.name,
            lastname=user_create.lastname,
            role=user_create.role,
            contract=user_create.contract,
        )

        user_created: User = await self.repository.create_user(user_create=user)

        client: EmailClient = EmailClient()

        actual_year: int = datetime.now().year

        email_information = UserCreatedEmail(
            frontend_url=configuration.FRONTEND_URL,
            year=actual_year,
            **user_create.model_dump(),
        )

        await client.send_email(
            subject="Bienvenido a Studeeo!!",
            email=user_create.email,
            email_information=email_information,
            template_name=TemplateHTML.VERIFICATION,
        )

        return user_created

    async def get_external_users(self) -> List[TeacherOdoo]:
        teacher_ids: Set[int] = {
            user.external_reference
            for user in await self.get_users(is_active=True)
            if user.external_reference
        }

        all_teachers: Set[int] = self.external_repository.get_teachers_ids()

        teachers_not_mapped: Set[int] = all_teachers.difference(teacher_ids)

        return self.external_repository.get_teachers(teachers_ids=teachers_not_mapped)

    async def get_users(self, is_active: bool) -> List[UserDB]:
        users: Sequence[User] = await self.repository.get_users(is_active=is_active)

        users_db: List[UserDB] = []

        for user in users:
            if not user.contract:
                continue

            users_db.append(
                UserDB(
                    id=user.id,
                    lastname=user.lastname,
                    name=user.name,
                    email=user.email,
                    role=user.role.name,
                    external_reference=user.external_reference,
                    contract=ContractDTO(
                        percentaje=user.contract.percentaje,
                        valid_from=user.contract.valid_from,
                        valid_to=user.contract.valid_to,
                    ),
                )
            )

        return users_db
