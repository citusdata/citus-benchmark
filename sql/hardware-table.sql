CREATE TABLE HARDWARE(
   resource_group CHAR(50) PRIMARY KEY NOT NULL,
   driver_hw   CHAR(30) NOT NULL,
   coord_hw CHAR(30) NOT NULL,
   worker_hw   CHAR(30) NOT NULL,
   coord_vcpu_num INT   NOT NULL,
   worker_vcp_num INT NOT NULL,
   coord_storage  INT NOT NULL,
   worker_storage INT   NOT NULL,
   workers  INT  NOT NULL
);
