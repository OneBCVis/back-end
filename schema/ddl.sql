create table if not exists block
(
    block_hash          varchar(128)    not null,
    previous_block_hash varchar(128)    not null,
    timestamp           varchar(32)     not null,
    miner               varchar(128),
    insert_time         timestamp       not null default current_timestamp,
    primary key (block_hash)
);

create table if not exists transaction
(
    txn_hash    varchar(128)                            not null,
    status      enum('PENDING', 'APPROVED', 'REJECTED') not null default 'PENDING',
    amount      int(16)                                 not null,
    primary key (txn_hash)
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
