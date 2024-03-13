create table if not exists block
(
    block_hash          varchar(128)    not null,
    previous_block_hash varchar(128)    not null,
    height              int             not null,
    nonce               int             not null,
    difficulty          int             not null,
    miner               varchar(128),
    time_stamp          varchar(32)     not null,
    insert_time         timestamp(3)    not null default current_timestamp(3),
    primary key (block_hash)
);

create table if not exists uncle
(
    uncle_hash          varchar(128)    not null,
    block_hash          varchar(128)    not null,
    primary key (uncle_hash),
    foreign key (block_hash) references block(block_hash)
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
    insert_time timestamp(3)                            not null default current_timestamp(3),
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

create procedure insert_transaction(
    in t_hash varchar(128),
    in t_status enum('PENDING', 'APPROVED', 'REJECTED'),
    in t_amount int,
    in t_type int,
    in t_nonce int,
    in t_fee int,
    in t_senders json,
    in t_receivers json,
    in is_full boolean,
    out result int
)
ist: begin
    declare i int default 0;
    declare sender varchar(128);
    declare receiver varchar(128);

    if (select count(*) from transaction where txn_hash = t_hash) = 0 then
        insert into transaction (txn_hash, status, amount, type, nonce, fee)
            values (t_hash, t_status, t_amount, t_type, t_nonce, t_fee);

        set i = 0;
        while i < json_length(t_senders) do
            set sender = json_extract(t_senders, concat('$[', i, ']'));
            insert into txn_sender (txn_hash, sender_key) values (t_hash, sender);
            set i = i + 1;
        end while;

        set i = 0;
        while i < json_length(t_receivers) do
            set receiver = json_extract(t_receivers, concat('$[', i, ']'));
            insert into txn_receiver (txn_hash, receiver_key) values (t_hash, receiver);
            set i = i + 1;
        end while;

        set result = 0;
        leave ist;
    else
        if is_full then
            update transaction
                set
                    status = t_status,
                    fee = t_fee
                where txn_hash = t_hash;
            set result = 1;
            leave ist;
        else
            set result = 2;
            leave ist;
        end if;
    end if;
    set result = -1;
    leave ist;
end;
