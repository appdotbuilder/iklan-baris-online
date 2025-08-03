from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from datetime import date as date_type
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for status fields
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AdStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DELETED = "deleted"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class MembershipStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class PaymentType(str, Enum):
    MEMBERSHIP = "membership"
    AD_BOOST = "ad_boost"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    profile_image: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ads: List["Ad"] = Relationship(back_populates="user")
    user_memberships: List["UserMembership"] = Relationship(back_populates="user")
    payments: List["Payment"] = Relationship(back_populates="user")
    ad_statistics: List["AdStatistic"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ads: List["Ad"] = Relationship(back_populates="category")


class MembershipPackage(SQLModel, table=True):
    __tablename__ = "membership_packages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    duration_days: int = Field(description="Duration in days")
    max_ads: int = Field(description="Maximum number of ads allowed")
    boost_credits: int = Field(default=0, description="Number of boost credits included")
    priority_support: bool = Field(default=False)
    features: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user_memberships: List["UserMembership"] = Relationship(back_populates="package")
    payments: List["Payment"] = Relationship(back_populates="membership_package")


class UserMembership(SQLModel, table=True):
    __tablename__ = "user_memberships"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    package_id: int = Field(foreign_key="membership_packages.id")
    status: MembershipStatus = Field(default=MembershipStatus.ACTIVE)
    start_date: date_type = Field(default_factory=date_type.today)
    end_date: date_type
    remaining_boost_credits: int = Field(default=0)
    remaining_ads: int = Field(default=0)
    auto_renew: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="user_memberships")
    package: MembershipPackage = Relationship(back_populates="user_memberships")


class Ad(SQLModel, table=True):
    __tablename__ = "ads"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: int = Field(foreign_key="categories.id")
    title: str = Field(max_length=200)
    description: str = Field(max_length=5000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=15)
    price_negotiable: bool = Field(default=False)
    location: Optional[str] = Field(default=None, max_length=200)
    contact_info: Optional[str] = Field(default=None, max_length=500)
    images: List[str] = Field(default=[], sa_column=Column(JSON))
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    status: AdStatus = Field(default=AdStatus.DRAFT)
    is_boosted: bool = Field(default=False)
    boost_expires_at: Optional[datetime] = Field(default=None)
    views_count: int = Field(default=0)
    contact_count: int = Field(default=0)
    featured: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="ads")
    category: Category = Relationship(back_populates="ads")
    statistics: List["AdStatistic"] = Relationship(back_populates="ad")
    boost_payments: List["Payment"] = Relationship(back_populates="boosted_ad")


class AdStatistic(SQLModel, table=True):
    __tablename__ = "ad_statistics"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    ad_id: int = Field(foreign_key="ads.id")
    user_id: int = Field(foreign_key="users.id")
    date: date_type = Field(default_factory=date_type.today)
    views: int = Field(default=0)
    contacts: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ad: Ad = Relationship(back_populates="statistics")
    user: User = Relationship(back_populates="ad_statistics")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    membership_package_id: Optional[int] = Field(default=None, foreign_key="membership_packages.id")
    boosted_ad_id: Optional[int] = Field(default=None, foreign_key="ads.id")
    payment_type: PaymentType
    amount: Decimal = Field(decimal_places=2, max_digits=12)
    currency: str = Field(default="IDR", max_length=3)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    midtrans_order_id: str = Field(max_length=255, unique=True)
    midtrans_transaction_id: Optional[str] = Field(default=None, max_length=255)
    payment_method: Optional[str] = Field(default=None, max_length=100)
    payment_details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    paid_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="payments")
    membership_package: Optional[MembershipPackage] = Relationship(back_populates="payments")
    boosted_ad: Optional[Ad] = Relationship(back_populates="boost_payments")


class SystemSetting(SQLModel, table=True):
    __tablename__ = "system_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(max_length=100, unique=True)
    value: str = Field(max_length=1000)
    description: Optional[str] = Field(default=None, max_length=500)
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    full_name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    profile_image: Optional[str] = Field(default=None, max_length=500)


class UserLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(max_length=100)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default=None, max_length=100)
    sort_order: int = Field(default=0)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)


class MembershipPackageCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    duration_days: int
    max_ads: int
    boost_credits: int = Field(default=0)
    priority_support: bool = Field(default=False)
    features: Dict[str, Any] = Field(default={})


class MembershipPackageUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    duration_days: Optional[int] = Field(default=None)
    max_ads: Optional[int] = Field(default=None)
    boost_credits: Optional[int] = Field(default=None)
    priority_support: Optional[bool] = Field(default=None)
    features: Optional[Dict[str, Any]] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class AdCreate(SQLModel, table=False):
    category_id: int
    title: str = Field(max_length=200)
    description: str = Field(max_length=5000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=15)
    price_negotiable: bool = Field(default=False)
    location: Optional[str] = Field(default=None, max_length=200)
    contact_info: Optional[str] = Field(default=None, max_length=500)
    images: List[str] = Field(default=[])
    tags: List[str] = Field(default=[])


class AdUpdate(SQLModel, table=False):
    category_id: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=15)
    price_negotiable: Optional[bool] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=200)
    contact_info: Optional[str] = Field(default=None, max_length=500)
    images: Optional[List[str]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    status: Optional[AdStatus] = Field(default=None)


class AdBoost(SQLModel, table=False):
    ad_id: int
    duration_days: int = Field(ge=1, le=30, description="Boost duration in days (1-30)")


class PaymentCreate(SQLModel, table=False):
    payment_type: PaymentType
    membership_package_id: Optional[int] = Field(default=None)
    boosted_ad_id: Optional[int] = Field(default=None)
    amount: Decimal = Field(decimal_places=2, max_digits=12)


class PaymentCallback(SQLModel, table=False):
    order_id: str
    transaction_status: str
    transaction_id: Optional[str] = Field(default=None)
    payment_type: Optional[str] = Field(default=None)
    gross_amount: Optional[str] = Field(default=None)
    signature_key: Optional[str] = Field(default=None)


class UserStatistics(SQLModel, table=False):
    total_ads: int
    active_ads: int
    total_views: int
    total_contacts: int
    boost_credits_remaining: int
    membership_expires_at: Optional[datetime] = Field(default=None)


class AdminDashboardStats(SQLModel, table=False):
    total_users: int
    total_ads: int
    active_ads: int
    pending_ads: int
    total_payments: int
    total_revenue: Decimal
    active_memberships: int
