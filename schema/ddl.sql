create table if not exists block
(
    block_hash          varchar(128)    not null,
    previous_block_hash varchar(128)    not null,
    height              int             not null,
    nonce               int             not null,
    difficulty          int             not null,
    miner               varchar(128),
    time_stamp          varchar(32)     not null,
    insert_time         timestamp       not null default current_timestamp,
    primary key (block_hash)
);

create table if not exists uncle
(
    uncle_hash          varchar(128)    not null,
    block_hash          varchar(128)    not null,
    primary key (uncle_hash),
    foreign key (block_hash) references block(block_hash)
        on delete cascade,
    foreign key (uncle_hash) references block(block_hash)
        on delete cascade
);

create table if not exists off_chain_data
(
    block_hash          varchar(128)    not null,
    id                  varchar(128)    not null,
    txn_id              varchar(128),
    size                int             not null,
    primary key (block_hash, id),
    foreign key (block_hash) references block(block_hash)
        on delete cascade
);

create table if not exists txn_type
(
    type       int         not null,
    name       varchar(32) not null,
    primary key (type)
);

create table if not exists transaction
(
    txn_hash    varchar(128)                            not null,
    status      enum('PENDING', 'APPROVED', 'REJECTED') not null default 'PENDING',
    amount      int                                     not null,
    type        int                                     not null,
    nonce       int                                     not null,
    fee         int                                     not null,
    insert_time timestamp                               not null default current_timestamp,
    primary key (txn_hash),
    foreign key (type) references txn_type(type)
);

create table if not exists txn_sender
(
    txn_hash    varchar(128) not null,
    sender_key  varchar(128) not null,
    primary key (txn_hash, sender_key),
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);

create table if not exists txn_receiver
(
    txn_hash        varchar(128) not null,
    receiver_key    varchar(128) not null,
    primary key (txn_hash, receiver_key),
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);

create table if not exists block_txn
(
    block_hash  varchar(128) not null,
    txn_hash    varchar(128) not null,
    primary key (txn_hash),
    foreign key (block_hash) references block(block_hash)
        on delete cascade,
    foreign key (txn_hash) references transaction(txn_hash)
        on delete cascade
);
